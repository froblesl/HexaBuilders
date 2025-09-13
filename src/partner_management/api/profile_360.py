from flask import Blueprint, request, jsonify
from datetime import datetime
import asyncio
import aiohttp

profile_360_bp = Blueprint('profile_360', __name__)


class ServiceClient:
    """HTTP client for calling other microservices"""
    
    def __init__(self):
        self.onboarding_url = "http://onboarding:5001"
        self.recruitment_url = "http://recruitment:5002"
        self.campaign_url = "http://campaign-management:5003"
        self.timeout = 5.0  # 5 second timeout
    
    async def get_partner_contracts(self, partner_id: str):
        """Get contracts from Onboarding service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.onboarding_url}/contracts-query/partner/{partner_id}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('contracts', [])
                    return []
        except Exception as e:
            print(f"Error fetching contracts: {str(e)}")
            return []
    
    async def get_partner_jobs(self, partner_id: str):
        """Get jobs from Recruitment service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.recruitment_url}/jobs?partner_id={partner_id}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('jobs', [])
                    return []
        except Exception as e:
            print(f"Error fetching jobs: {str(e)}")
            return []
    
    async def get_partner_campaigns(self, partner_id: str):
        """Get campaigns from Campaign Management service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.campaign_url}/campaigns-query/partner/{partner_id}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('campaigns', [])
                    return []
        except Exception as e:
            print(f"Error fetching campaigns: {str(e)}")
            return []


@profile_360_bp.route('/<partner_id>/profile-360', methods=['GET'])
async def get_partner_profile_360(partner_id):
    """Get complete 360-degree partner profile"""
    try:
        # Initialize service client
        service_client = ServiceClient()
        
        # TODO: Get partner basic data from local repository
        partner_data = {
            "id": partner_id,
            "name": "Example Partner",
            "email": "partner@example.com",
            "status": "ACTIVE",
            "tier": "GOLD",
            "registration_date": "2024-01-15T10:30:00Z",
            "last_activity": "2024-01-19T15:45:00Z"
        }
        
        # Fetch data from all services concurrently
        contracts_task = service_client.get_partner_contracts(partner_id)
        jobs_task = service_client.get_partner_jobs(partner_id)
        campaigns_task = service_client.get_partner_campaigns(partner_id)
        
        # Wait for all requests to complete
        contracts, jobs, campaigns = await asyncio.gather(
            contracts_task,
            jobs_task,
            campaigns_task,
            return_exceptions=True
        )
        
        # Handle exceptions in results
        if isinstance(contracts, Exception):
            contracts = []
        if isinstance(jobs, Exception):
            jobs = []
        if isinstance(campaigns, Exception):
            campaigns = []
        
        # Calculate aggregated metrics
        total_campaigns = len(campaigns)
        active_campaigns = len([c for c in campaigns if c.get('status') == 'ACTIVE'])
        total_jobs_posted = len(jobs)
        active_contracts = len([c for c in contracts if c.get('is_active', False)])
        
        # Build comprehensive profile
        profile_360 = {
            "partner": partner_data,
            "summary": {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_jobs_posted": total_jobs_posted,
                "active_contracts": active_contracts,
                "last_campaign_activity": campaigns[0].get('updated_at') if campaigns else None,
                "last_hiring_activity": jobs[0].get('updated_at') if jobs else None
            },
            "contracts": {
                "total": len(contracts),
                "active": active_contracts,
                "details": contracts[:5]  # Limit to 5 most recent
            },
            "recruitment": {
                "total_jobs": total_jobs_posted,
                "active_jobs": len([j for j in jobs if j.get('status') == 'OPEN']),
                "recent_jobs": jobs[:5]  # Limit to 5 most recent
            },
            "campaigns": {
                "total": total_campaigns,
                "active": active_campaigns,
                "recent_campaigns": campaigns[:5],  # Limit to 5 most recent
                "performance_summary": _calculate_campaign_performance_summary(campaigns)
            },
            "engagement_score": _calculate_engagement_score(contracts, jobs, campaigns),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return jsonify(profile_360), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@profile_360_bp.route('/<partner_id>/validation-status', methods=['GET'])
def get_partner_validation_status(partner_id):
    """Get partner validation status for other services"""
    try:
        # TODO: Implement actual validation logic
        validation_status = {
            "partner_id": partner_id,
            "is_validated": True,
            "is_active": True,
            "can_create_campaigns": True,
            "can_post_jobs": True,
            "verification_level": "VERIFIED",
            "tier": "GOLD",
            "restrictions": [],
            "permissions": {
                "max_campaign_budget": 50000.00,
                "max_concurrent_jobs": 10,
                "can_access_premium_features": True
            },
            "last_validated": "2024-01-15T10:30:00Z"
        }
        
        return jsonify(validation_status), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@profile_360_bp.route('/<partner_id>/metrics/dashboard', methods=['GET'])
async def get_partner_dashboard_metrics(partner_id):
    """Get dashboard metrics for partner"""
    try:
        service_client = ServiceClient()
        
        # Get data from services
        campaigns_task = service_client.get_partner_campaigns(partner_id)
        jobs_task = service_client.get_partner_jobs(partner_id)
        
        campaigns, jobs = await asyncio.gather(
            campaigns_task,
            jobs_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(campaigns, Exception):
            campaigns = []
        if isinstance(jobs, Exception):
            jobs = []
        
        # Calculate dashboard metrics
        dashboard_metrics = {
            "partner_id": partner_id,
            "campaigns": {
                "total": len(campaigns),
                "active": len([c for c in campaigns if c.get('status') == 'ACTIVE']),
                "total_spend": sum(c.get('budget_spent', 0) for c in campaigns),
                "average_performance": _calculate_average_campaign_performance(campaigns)
            },
            "recruitment": {
                "total_jobs": len(jobs),
                "open_jobs": len([j for j in jobs if j.get('status') == 'OPEN']),
                "total_applications": sum(j.get('current_applications', 0) for j in jobs),
                "avg_applications_per_job": _calculate_avg_applications(jobs)
            },
            "engagement": {
                "score": _calculate_engagement_score([], jobs, campaigns),
                "trend": "increasing",  # TODO: Calculate actual trend
                "last_activity": _get_last_activity_date(jobs, campaigns)
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return jsonify(dashboard_metrics), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


def _calculate_campaign_performance_summary(campaigns):
    """Calculate summary of campaign performance"""
    if not campaigns:
        return {"total_impressions": 0, "total_clicks": 0, "total_conversions": 0, "average_ctr": 0}
    
    total_impressions = sum(c.get('performance_summary', {}).get('impressions', 0) for c in campaigns)
    total_clicks = sum(c.get('performance_summary', {}).get('clicks', 0) for c in campaigns)
    total_conversions = sum(c.get('performance_summary', {}).get('conversions', 0) for c in campaigns)
    
    average_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    return {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "total_conversions": total_conversions,
        "average_ctr": round(average_ctr, 2)
    }


def _calculate_average_campaign_performance(campaigns):
    """Calculate average campaign performance metrics"""
    if not campaigns:
        return {"ctr": 0, "conversion_rate": 0, "cost_per_conversion": 0}
    
    active_campaigns = [c for c in campaigns if c.get('status') == 'ACTIVE']
    if not active_campaigns:
        return {"ctr": 0, "conversion_rate": 0, "cost_per_conversion": 0}
    
    # Mock calculation - in real implementation, calculate from actual performance data
    return {
        "ctr": 3.2,
        "conversion_rate": 4.8,
        "cost_per_conversion": 45.67
    }


def _calculate_avg_applications(jobs):
    """Calculate average applications per job"""
    if not jobs:
        return 0
    
    total_applications = sum(j.get('current_applications', 0) for j in jobs)
    return round(total_applications / len(jobs), 1) if jobs else 0


def _calculate_engagement_score(contracts, jobs, campaigns):
    """Calculate partner engagement score"""
    score = 0
    
    # Base score
    score += min(len(contracts) * 10, 30)  # Max 30 points for contracts
    score += min(len(jobs) * 5, 25)       # Max 25 points for jobs
    score += min(len(campaigns) * 8, 40)  # Max 40 points for campaigns
    
    # Activity bonus
    recent_activity = any([
        any(c.get('status') == 'ACTIVE' for c in campaigns),
        any(j.get('status') == 'OPEN' for j in jobs)
    ])
    
    if recent_activity:
        score += 5
    
    return min(score, 100)  # Cap at 100


def _get_last_activity_date(jobs, campaigns):
    """Get the most recent activity date"""
    dates = []
    
    for job in jobs:
        if job.get('updated_at'):
            dates.append(job['updated_at'])
    
    for campaign in campaigns:
        if campaign.get('updated_at'):
            dates.append(campaign['updated_at'])
    
    return max(dates) if dates else None