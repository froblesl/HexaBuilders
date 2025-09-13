class OnboardingDomainException(Exception):
    """Base exception for onboarding domain errors"""
    pass


class ContractException(OnboardingDomainException):
    """Base exception for contract-related errors"""
    pass


class ContractNotFoundException(ContractException):
    """Raised when a contract is not found"""
    pass


class ContractInvalidStateException(ContractException):
    """Raised when trying to perform an invalid operation on a contract"""
    pass


class ContractAlreadySignedException(ContractException):
    """Raised when trying to modify an already signed contract"""
    pass


class ContractValidationException(ContractException):
    """Raised when contract validation fails"""
    pass


class NegotiationException(OnboardingDomainException):
    """Base exception for negotiation-related errors"""
    pass


class NegotiationNotFoundException(NegotiationException):
    """Raised when a negotiation is not found"""
    pass


class NegotiationAlreadyCompletedException(NegotiationException):
    """Raised when trying to modify a completed negotiation"""
    pass


class InvalidProposalException(NegotiationException):
    """Raised when a proposal is invalid"""
    pass


class LegalException(OnboardingDomainException):
    """Base exception for legal-related errors"""
    pass


class LegalValidationFailedException(LegalException):
    """Raised when legal validation fails"""
    pass


class ComplianceViolationException(LegalException):
    """Raised when a compliance violation is detected"""
    pass


class DocumentException(OnboardingDomainException):
    """Base exception for document-related errors"""
    pass


class DocumentNotFoundException(DocumentException):
    """Raised when a document is not found"""
    pass


class InvalidSignatureException(DocumentException):
    """Raised when a signature is invalid"""
    pass


class DocumentAlreadySignedException(DocumentException):
    """Raised when trying to sign an already signed document"""
    pass


class UnsupportedDocumentTypeException(DocumentException):
    """Raised when an unsupported document type is used"""
    pass