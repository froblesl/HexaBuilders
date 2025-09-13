class CampaignManagementException(Exception):
    """Base exception for campaign management domain errors"""
    pass


class CampaignException(CampaignManagementException):
    """Base exception for campaign-related errors"""
    pass


class CampaignNotFoundException(CampaignException):
    """Raised when a campaign is not found"""
    pass


class InvalidCampaignDataException(CampaignException):
    """Raised when campaign data is invalid"""
    pass


class CampaignStateException(CampaignException):
    """Raised when trying to perform invalid operation based on campaign state"""
    pass


class BudgetException(CampaignManagementException):
    """Base exception for budget-related errors"""
    pass


class InsufficientBudgetException(BudgetException):
    """Raised when budget is insufficient for operation"""
    pass


class BudgetExceededException(BudgetException):
    """Raised when budget has been exceeded"""
    pass


class PerformanceException(CampaignManagementException):
    """Base exception for performance-related errors"""
    pass


class InvalidMetricsException(PerformanceException):
    """Raised when performance metrics are invalid"""
    pass


class TargetingException(CampaignManagementException):
    """Base exception for targeting-related errors"""
    pass


class InvalidTargetingException(TargetingException):
    """Raised when targeting parameters are invalid"""
    pass