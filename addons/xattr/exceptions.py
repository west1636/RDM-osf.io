from addons.base.exceptions import AddonError


class XattrError(AddonError):
    """Base exception class for Xattr-related error."""
    pass

class NameEmptyError(XattrError):
    """Raised if user tries to provide an empty name value."""
    pass

class NameInvalidError(XattrError):
    """Raised if user tries to provide a string containing an invalid character."""
    pass

class NameMaximumLengthError(XattrError):
    """Raised if user tries to provide a name which exceeds the maximum accepted length."""
    pass

class PageCannotRenameError(XattrError):
    """Raised if user tried to rename special xattr pages, e.g. home."""
    pass

class PageConflictError(XattrError):
    """Raised if user tries to use an existing xattr page name."""
    pass

class PageNotFoundError(XattrError):
    """Raised if user tries to access a xattr page that does not exist."""
    pass

class InvalidVersionError(XattrError):
    """Raised if user tries to access a xattr page version that does not exist."""
    pass
