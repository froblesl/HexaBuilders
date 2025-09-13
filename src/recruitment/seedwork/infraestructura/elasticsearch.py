import json
from typing import Dict, Any, List, Optional
from elasticsearch import Elasticsearch, NotFoundError
from datetime import datetime

from recruitment.seedwork.dominio.entidades import SearchRepository
from recruitment.seedwork.dominio.excepciones import SearchIndexException, InvalidSearchQueryException


class ElasticsearchRepository(SearchRepository):
    def __init__(self, elasticsearch_url: str):
        self.es = Elasticsearch([elasticsearch_url])
        self.candidates_index = "candidates"
        self.jobs_index = "jobs"
    
    async def setup_indices(self):
        """Setup Elasticsearch indices with mappings"""
        try:
            # Candidates index mapping
            candidates_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {"keyword": {"type": "keyword"}}
                        },
                        "email": {"type": "keyword"},
                        "skills": {"type": "keyword"},
                        "technical_skills": {"type": "keyword"},
                        "experience_level": {"type": "keyword"},
                        "total_experience_years": {"type": "integer"},
                        "availability": {"type": "keyword"},
                        "summary": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "location": {
                            "properties": {
                                "city": {"type": "keyword"},
                                "country": {"type": "keyword"},
                                "remote_friendly": {"type": "boolean"}
                            }
                        },
                        "salary_expectation": {
                            "properties": {
                                "min": {"type": "float"},
                                "max": {"type": "float"},
                                "currency": {"type": "keyword"}
                            }
                        },
                        "work_experience": {
                            "type": "nested",
                            "properties": {
                                "company": {"type": "text"},
                                "position": {"type": "text"},
                                "technologies": {"type": "keyword"},
                                "is_current": {"type": "boolean"}
                            }
                        },
                        "education": {
                            "type": "nested",
                            "properties": {
                                "institution": {"type": "text"},
                                "degree": {"type": "text"},
                                "field_of_study": {"type": "text"}
                            }
                        },
                        "certifications": {"type": "keyword"},
                        "languages": {
                            "type": "nested",
                            "properties": {
                                "name": {"type": "keyword"},
                                "level": {"type": "keyword"}
                            }
                        },
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }
            
            # Jobs index mapping
            jobs_mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "standard",
                            "fields": {"keyword": {"type": "keyword"}}
                        },
                        "description": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "partner_id": {"type": "keyword"},
                        "status": {"type": "keyword"},
                        "job_type": {"type": "keyword"},
                        "department": {"type": "keyword"},
                        "required_skills": {"type": "keyword"},
                        "nice_to_have_skills": {"type": "keyword"},
                        "experience_level": {"type": "keyword"},
                        "min_experience_years": {"type": "integer"},
                        "max_experience_years": {"type": "integer"},
                        "location": {
                            "properties": {
                                "city": {"type": "keyword"},
                                "country": {"type": "keyword"},
                                "is_remote": {"type": "boolean"},
                                "is_hybrid": {"type": "boolean"}
                            }
                        },
                        "salary_range": {
                            "properties": {
                                "min": {"type": "float"},
                                "max": {"type": "float"},
                                "currency": {"type": "keyword"}
                            }
                        },
                        "benefits": {"type": "keyword"},
                        "perks": {"type": "keyword"},
                        "tags": {"type": "keyword"},
                        "posted_date": {"type": "date"},
                        "application_deadline": {"type": "date"},
                        "max_applications": {"type": "integer"},
                        "current_applications": {"type": "integer"},
                        "created_at": {"type": "date"},
                        "updated_at": {"type": "date"}
                    }
                }
            }
            
            # Create indices
            if not self.es.indices.exists(index=self.candidates_index):
                self.es.indices.create(index=self.candidates_index, body=candidates_mapping)
            
            if not self.es.indices.exists(index=self.jobs_index):
                self.es.indices.create(index=self.jobs_index, body=jobs_mapping)
                
        except Exception as e:
            raise SearchIndexException(f"Failed to setup indices: {str(e)}")
    
    async def index_document(self, document_id: str, document: Dict[str, Any], index: str = None):
        """Index a document"""
        try:
            if not index:
                # Determine index based on document type
                if 'skills' in document and 'availability' in document:
                    index = self.candidates_index
                elif 'title' in document and 'partner_id' in document:
                    index = self.jobs_index
                else:
                    raise InvalidSearchQueryException("Cannot determine document type")
            
            response = self.es.index(
                index=index,
                id=document_id,
                body=document
            )
            return response
            
        except Exception as e:
            raise SearchIndexException(f"Failed to index document: {str(e)}")
    
    async def search_documents(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        size: int = 10,
        offset: int = 0,
        index: str = None
    ) -> Dict[str, Any]:
        """Search documents"""
        try:
            if not index:
                index = self.candidates_index  # Default to candidates
            
            # Build search query
            search_body = {
                "query": self._build_query(query, filters),
                "size": size,
                "from": offset,
                "sort": [
                    {"_score": {"order": "desc"}},
                    {"updated_at": {"order": "desc"}}
                ]
            }
            
            response = self.es.search(
                index=index,
                body=search_body
            )
            
            return {
                "total": response["hits"]["total"]["value"],
                "documents": [hit["_source"] for hit in response["hits"]["hits"]],
                "scores": [hit["_score"] for hit in response["hits"]["hits"]]
            }
            
        except Exception as e:
            raise SearchIndexException(f"Failed to search documents: {str(e)}")
    
    def _build_query(self, query: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build Elasticsearch query"""
        if not query and not filters:
            return {"match_all": {}}
        
        must_clauses = []
        filter_clauses = []
        
        # Text search
        if query:
            must_clauses.append({
                "multi_match": {
                    "query": query,
                    "fields": [
                        "name^2", "title^2", "summary", "description",
                        "skills^1.5", "technical_skills^1.5",
                        "work_experience.company", "work_experience.position",
                        "education.institution", "education.degree"
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if key == "skills":
                    if isinstance(value, list):
                        filter_clauses.append({
                            "terms": {"skills": value}
                        })
                    else:
                        filter_clauses.append({
                            "term": {"skills": value}
                        })
                
                elif key == "experience_level":
                    filter_clauses.append({
                        "term": {"experience_level": value}
                    })
                
                elif key == "availability":
                    filter_clauses.append({
                        "term": {"availability": value}
                    })
                
                elif key == "min_experience_years":
                    filter_clauses.append({
                        "range": {"total_experience_years": {"gte": value}}
                    })
                
                elif key == "max_experience_years":
                    filter_clauses.append({
                        "range": {"total_experience_years": {"lte": value}}
                    })
                
                elif key == "location":
                    location_clauses = []
                    if value.get("city"):
                        location_clauses.append({
                            "term": {"location.city": value["city"]}
                        })
                    if value.get("country"):
                        location_clauses.append({
                            "term": {"location.country": value["country"]}
                        })
                    if value.get("remote_friendly"):
                        location_clauses.append({
                            "term": {"location.remote_friendly": True}
                        })
                    
                    if location_clauses:
                        filter_clauses.append({
                            "bool": {"should": location_clauses}
                        })
                
                elif key == "salary_range":
                    if value.get("min"):
                        filter_clauses.append({
                            "range": {"salary_expectation.max": {"gte": value["min"]}}
                        })
                    if value.get("max"):
                        filter_clauses.append({
                            "range": {"salary_expectation.min": {"lte": value["max"]}}
                        })
                
                elif key == "job_type":
                    filter_clauses.append({
                        "term": {"job_type": value}
                    })
                
                elif key == "status":
                    filter_clauses.append({
                        "term": {"status": value}
                    })
                
                elif key == "partner_id":
                    filter_clauses.append({
                        "term": {"partner_id": value}
                    })
        
        # Combine query and filters
        if must_clauses and filter_clauses:
            return {
                "bool": {
                    "must": must_clauses,
                    "filter": filter_clauses
                }
            }
        elif must_clauses:
            return {"bool": {"must": must_clauses}}
        elif filter_clauses:
            return {"bool": {"filter": filter_clauses}}
        else:
            return {"match_all": {}}
    
    async def update_document(self, document_id: str, document: Dict[str, Any], index: str = None):
        """Update a document"""
        try:
            if not index:
                # Try to determine index
                if 'skills' in document and 'availability' in document:
                    index = self.candidates_index
                elif 'title' in document and 'partner_id' in document:
                    index = self.jobs_index
                else:
                    raise InvalidSearchQueryException("Cannot determine document type")
            
            response = self.es.update(
                index=index,
                id=document_id,
                body={"doc": document}
            )
            return response
            
        except NotFoundError:
            # Document doesn't exist, create it
            return await self.index_document(document_id, document, index)
        except Exception as e:
            raise SearchIndexException(f"Failed to update document: {str(e)}")
    
    async def delete_document(self, document_id: str, index: str = None):
        """Delete a document"""
        try:
            if not index:
                # Try both indices
                try:
                    self.es.delete(index=self.candidates_index, id=document_id)
                except NotFoundError:
                    self.es.delete(index=self.jobs_index, id=document_id)
            else:
                self.es.delete(index=index, id=document_id)
                
        except NotFoundError:
            pass  # Document doesn't exist, which is fine
        except Exception as e:
            raise SearchIndexException(f"Failed to delete document: {str(e)}")
    
    async def search_candidates(
        self, 
        query: str = "", 
        filters: Dict[str, Any] = None,
        size: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search candidates specifically"""
        return await self.search_documents(
            query=query,
            filters=filters,
            size=size,
            offset=offset,
            index=self.candidates_index
        )
    
    async def search_jobs(
        self, 
        query: str = "", 
        filters: Dict[str, Any] = None,
        size: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Search jobs specifically"""
        return await self.search_documents(
            query=query,
            filters=filters,
            size=size,
            offset=offset,
            index=self.jobs_index
        )
    
    async def get_aggregations(self, index: str, field: str) -> Dict[str, Any]:
        """Get aggregations for a field"""
        try:
            search_body = {
                "size": 0,
                "aggs": {
                    f"{field}_agg": {
                        "terms": {
                            "field": field,
                            "size": 100
                        }
                    }
                }
            }
            
            response = self.es.search(index=index, body=search_body)
            return response["aggregations"][f"{field}_agg"]["buckets"]
            
        except Exception as e:
            raise SearchIndexException(f"Failed to get aggregations: {str(e)}")
    
    async def suggest_candidates(self, job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest candidates based on job requirements"""
        filters = {}
        
        if job_requirements.get("required_skills"):
            filters["skills"] = job_requirements["required_skills"]
        
        if job_requirements.get("experience_level"):
            filters["experience_level"] = job_requirements["experience_level"]
        
        if job_requirements.get("min_experience_years"):
            filters["min_experience_years"] = job_requirements["min_experience_years"]
        
        if job_requirements.get("location"):
            filters["location"] = job_requirements["location"]
        
        # Always filter for available candidates
        filters["availability"] = "AVAILABLE"
        
        # Build query for better matching
        query_terms = []
        if job_requirements.get("required_skills"):
            query_terms.extend(job_requirements["required_skills"])
        if job_requirements.get("job_title"):
            query_terms.append(job_requirements["job_title"])
        
        query = " ".join(query_terms)
        
        result = await self.search_candidates(
            query=query,
            filters=filters,
            size=50  # Get more candidates for scoring
        )
        
        return result["documents"]