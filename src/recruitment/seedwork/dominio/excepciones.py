class RecruitmentDomainException(Exception):
    """Base exception for recruitment domain errors"""
    pass


class CandidateException(RecruitmentDomainException):
    """Base exception for candidate-related errors"""
    pass


class CandidateNotFoundException(CandidateException):
    """Raised when a candidate is not found"""
    pass


class CandidateAlreadyExistsException(CandidateException):
    """Raised when trying to create a candidate that already exists"""
    pass


class CandidateNotAvailableException(CandidateException):
    """Raised when trying to assign an unavailable candidate"""
    pass


class InvalidCandidateDataException(CandidateException):
    """Raised when candidate data is invalid"""
    pass


class JobException(RecruitmentDomainException):
    """Base exception for job-related errors"""
    pass


class JobNotFoundException(JobException):
    """Raised when a job is not found"""
    pass


class JobAlreadyClosedException(JobException):
    """Raised when trying to modify a closed job"""
    pass


class InvalidJobDataException(JobException):
    """Raised when job data is invalid"""
    pass


class JobApplicationException(RecruitmentDomainException):
    """Base exception for job application errors"""
    pass


class ApplicationNotFoundException(JobApplicationException):
    """Raised when an application is not found"""
    pass


class DuplicateApplicationException(JobApplicationException):
    """Raised when a candidate tries to apply to the same job twice"""
    pass


class InvalidApplicationStatusException(JobApplicationException):
    """Raised when trying to set an invalid application status"""
    pass


class MatchingException(RecruitmentDomainException):
    """Base exception for matching-related errors"""
    pass


class NoMatchesFoundException(MatchingException):
    """Raised when no matches are found for a job"""
    pass


class InvalidMatchingCriteriaException(MatchingException):
    """Raised when matching criteria are invalid"""
    pass


class InterviewException(RecruitmentDomainException):
    """Base exception for interview-related errors"""
    pass


class InterviewNotFoundException(InterviewException):
    """Raised when an interview is not found"""
    pass


class InterviewAlreadyCompletedException(InterviewException):
    """Raised when trying to modify a completed interview"""
    pass


class InvalidInterviewTimeException(InterviewException):
    """Raised when interview time is invalid"""
    pass


class SearchException(RecruitmentDomainException):
    """Base exception for search-related errors"""
    pass


class SearchIndexException(SearchException):
    """Raised when there's an error with search indexing"""
    pass


class InvalidSearchQueryException(SearchException):
    """Raised when search query is invalid"""
    pass