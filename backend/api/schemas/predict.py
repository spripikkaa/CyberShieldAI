from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictRequest(BaseModel):
    """Numerical features extracted from a URL for phishing classification."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    URLLength: float = Field(..., ge=0, description="Total character length of the URL.")
    DomainLength: float = Field(..., ge=0, description="Character length of the domain.")
    IsDomainIP: float = Field(..., ge=0, le=1, description="1 if domain is an IP address, else 0.")
    URLSimilarityIndex: float = Field(..., ge=0, description="Similarity score between URL and domain.")
    CharContinuationRate: float = Field(..., ge=0, description="Rate of continuing character sequences.")
    TLDLegitimateProb: float = Field(..., ge=0, le=1, description="Estimated legitimacy probability of the TLD.")
    URLCharProb: float = Field(..., ge=0, le=1, description="Character probability score for the URL.")
    TLDLength: float = Field(..., ge=0, description="Length of the top-level domain.")
    NoOfSubDomain: float = Field(..., ge=0, description="Number of subdomains.")
    HasObfuscation: float = Field(..., ge=0, le=1, description="1 if URL obfuscation is detected, else 0.")
    NoOfObfuscatedChar: float = Field(..., ge=0, description="Count of obfuscated characters.")
    ObfuscationRatio: float = Field(..., ge=0, description="Ratio of obfuscated characters in the URL.")
    NoOfLettersInURL: float = Field(..., ge=0, description="Count of alphabetic characters.")
    LetterRatioInURL: float = Field(..., ge=0, description="Ratio of alphabetic characters.")
    NoOfDegitsInURL: float = Field(..., ge=0, description="Count of numeric characters.")
    DegitRatioInURL: float = Field(..., ge=0, description="Ratio of numeric characters.")
    NoOfEqualsInURL: float = Field(..., ge=0, description="Count of '=' characters.")
    NoOfQMarkInURL: float = Field(..., ge=0, description="Count of '?' characters.")
    NoOfAmpersandInURL: float = Field(..., ge=0, description="Count of '&' characters.")
    NoOfOtherSpecialCharsInURL: float = Field(..., ge=0, description="Count of other special characters.")
    SpacialCharRatioInURL: float = Field(..., ge=0, description="Ratio of special characters.")
    IsHTTPS: float = Field(..., ge=0, le=1, description="1 if HTTPS is used, else 0.")
    LineOfCode: float = Field(..., ge=0, description="Number of HTML source lines.")
    LargestLineLength: float = Field(..., ge=0, description="Length of the longest HTML line.")
    HasTitle: float = Field(..., ge=0, le=1, description="1 if the page has a title tag, else 0.")
    DomainTitleMatchScore: float = Field(..., ge=0, description="Match score between domain and page title.")
    URLTitleMatchScore: float = Field(..., ge=0, description="Match score between URL and page title.")
    HasFavicon: float = Field(..., ge=0, le=1, description="1 if a favicon is present, else 0.")
    Robots: float = Field(..., ge=0, le=1, description="1 if robots.txt is present, else 0.")
    IsResponsive: float = Field(..., ge=0, le=1, description="1 if the page is responsive, else 0.")
    NoOfURLRedirect: float = Field(..., ge=0, description="Number of URL redirects.")
    NoOfSelfRedirect: float = Field(..., ge=0, description="Number of self-redirects.")
    HasDescription: float = Field(..., ge=0, le=1, description="1 if meta description exists, else 0.")
    NoOfPopup: float = Field(..., ge=0, description="Number of popup elements.")
    NoOfiFrame: float = Field(..., ge=0, description="Number of iframe elements.")
    HasExternalFormSubmit: float = Field(..., ge=0, le=1, description="1 if external form submit exists, else 0.")
    HasSocialNet: float = Field(..., ge=0, le=1, description="1 if social network links exist, else 0.")
    HasSubmitButton: float = Field(..., ge=0, le=1, description="1 if a submit button exists, else 0.")
    HasHiddenFields: float = Field(..., ge=0, le=1, description="1 if hidden form fields exist, else 0.")
    HasPasswordField: float = Field(..., ge=0, le=1, description="1 if a password field exists, else 0.")
    Bank: float = Field(..., ge=0, le=1, description="1 if banking-related content is detected, else 0.")
    Pay: float = Field(..., ge=0, le=1, description="1 if payment-related content is detected, else 0.")
    Crypto: float = Field(..., ge=0, le=1, description="1 if crypto-related content is detected, else 0.")
    HasCopyrightInfo: float = Field(..., ge=0, le=1, description="1 if copyright info is present, else 0.")
    NoOfImage: float = Field(..., ge=0, description="Number of image tags.")
    NoOfCSS: float = Field(..., ge=0, description="Number of CSS references.")
    NoOfJS: float = Field(..., ge=0, description="Number of JavaScript references.")
    NoOfSelfRef: float = Field(..., ge=0, description="Number of self-referencing links.")
    NoOfEmptyRef: float = Field(..., ge=0, description="Number of empty href links.")
    NoOfExternalRef: float = Field(..., ge=0, description="Number of external references.")

    def to_feature_dict(self) -> dict[str, float]:
        """Serialize validated input into the dict format expected by the predictor."""
        return self.model_dump()


class PredictResponse(BaseModel):
    """Prediction result returned by the phishing classifier."""

    prediction: Literal["Legitimate", "Phishing"] = Field(
        ...,
        description="Final classification label.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence for the predicted class (0.0 to 1.0).",
    )
