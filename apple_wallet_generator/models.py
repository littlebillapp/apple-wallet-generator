# -*- coding: utf-8 -*-
import decimal
from enum import Enum
import hashlib
import json
import zipfile
from io import BytesIO

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from pydantic import BaseModel


class Alignment(str, Enum):
    LEFT = "PKTextAlignmentLeft"
    CENTER = "PKTextAlignmentCenter"
    RIGHT = "PKTextAlignmentRight"
    JUSTIFIED = "PKTextAlignmentJustified"
    NATURAL = "PKTextAlignmentNatural"


class BarcodeFormat:
    PDF417 = "PKBarcodeFormatPDF417"
    QR = "PKBarcodeFormatQR"
    AZTEC = "PKBarcodeFormatAztec"
    CODE128 = "PKBarcodeFormatCode128"


class TransitType:
    AIR = "PKTransitTypeAir"
    TRAIN = "PKTransitTypeTrain"
    BUS = "PKTransitTypeBus"
    BOAT = "PKTransitTypeBoat"
    GENERIC = "PKTransitTypeGeneric"


class DateStyle:
    NONE = "PKDateStyleNone"
    SHORT = "PKDateStyleShort"
    MEDIUM = "PKDateStyleMedium"
    LONG = "PKDateStyleLong"
    FULL = "PKDateStyleFull"


class NumberStyle:
    DECIMAL = "PKNumberStyleDecimal"
    PERCENT = "PKNumberStylePercent"
    SCIENTIFIC = "PKNumberStyleScientific"
    SPELLOUT = "PKNumberStyleSpellOut"


class BaseField(BaseModel):
    # Required. The key must be unique within the scope
    key: str
    # Required. Value of the field. For example, 42
    value: str
    # Optional. Label text for the field.
    label: str | None = ""
    # Optional. Format string for the alert text that is displayed when the pass is updated
    changeMessage: str | None = None
    # Optional. Text alignment of the field.
    textAlignment: Alignment = Alignment.LEFT

    def json_dict(self):
        return self.__dict__


class DateField(BaseField):

    def __init__(
        self,
        key,
        value,
        label="",
        dateStyle=DateStyle.SHORT,
        timeStyle=DateStyle.SHORT,
        ignoresTimeZone=False,
    ):
        super().__init__(key, value, label)
        self.dateStyle = dateStyle  # Style of date to display
        self.timeStyle = timeStyle  # Style of time to display
        self.isRelative = (
            False  # If true, the labels value is displayed as a relative date
        )
        if ignoresTimeZone:
            self.ignoresTimeZone = ignoresTimeZone

    def json_dict(self):
        return self.__dict__


class NumberField(BaseField):

    def __init__(self, key, value, label=""):
        super().__init__(key, value, label)
        self.numberStyle = NumberStyle.DECIMAL  # Style of date to display

    def json_dict(self):
        return self.__dict__


class CurrencyField(BaseField):

    def __init__(self, key, value, label="", currencyCode=""):
        super().__init__(key, value, label)
        self.currencyCode = currencyCode  # ISO 4217 currency code

    def json_dict(self):
        return self.__dict__


class Barcode(BaseModel):

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        message,
        format=BarcodeFormat.PDF417,
        altText="",
        messageEncoding="iso-8859-1",
    ):
        self.format = format
        self.message = (
            message  # Required. Message or payload to be displayed as a barcode
        )
        self.messageEncoding = messageEncoding  # Required. Text encoding that is used to convert the message
        if altText:
            self.altText = altText  # Optional. Text displayed near the barcode

    def json_dict(self):
        return self.__dict__


class Location(object):

    def __init__(self, latitude, longitude, altitude=0.0):
        # Required. Latitude, in degrees, of the location.
        try:
            self.latitude = float(latitude)
        except (ValueError, TypeError):
            self.latitude = 0.0
        # Required. Longitude, in degrees, of the location.
        try:
            self.longitude = float(longitude)
        except (ValueError, TypeError):
            self.longitude = 0.0
        # Optional. Altitude, in meters, of the location.
        try:
            self.altitude = float(altitude)
        except (ValueError, TypeError):
            self.altitude = 0.0
        # Optional. Notification distance
        self.distance = None
        # Optional. Text displayed on the lock screen when
        # the pass is currently near the location
        self.relevantText = ""

    def json_dict(self):
        return self.__dict__


class IBeacon(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    def __init__(self, proximityuuid, major, minor):
        # IBeacon data
        self.proximityUUID = proximityuuid
        self.major = major
        self.minor = minor

        # Optional. Text message where near the ibeacon
        self.relevantText = ""

    def json_dict(self):
        return self.__dict__


class PassInformation(BaseModel):
    jsonname: str | None = None

    headerFields: list[BaseField] = []
    primaryFields: list[BaseField] = []
    secondaryFields: list[BaseField] = []
    backFields: list[BaseField] = []
    auxiliaryFields: list[BaseField] = []

    class Config:
        arbitrary_types_allowed = True

    def addHeaderField(self, key: str, value: str, label: str | None = None):
        field = BaseField(key=key, value=value, label=label)
        self.headerFields.append(field)

    def addPrimaryField(self, key: str, value: str, label: str | None = None):
        field = BaseField(key=key, value=value, label=label)
        self.primaryFields.append(field)

    def addSecondaryField(self, key: str, value: str, label: str | None = None):
        field = BaseField(key=key, value=value, label=label)
        self.secondaryFields.append(field)

    def addBackField(self, key: str, value: str, label: str | None = None):
        field = BaseField(key=key, value=value, label=label)
        self.backFields.append(field)

    def addAuxiliaryField(self, key: str, value: str, label: str | None = None):
        field = BaseField(key=key, value=value, label=label)
        self.auxiliaryFields.append(field)

    def json_dict(self):
        d = {}
        if self.headerFields:
            d.update({"headerFields": [f.json_dict() for f in self.headerFields]})
        if self.primaryFields:
            d.update({"primaryFields": [f.json_dict() for f in self.primaryFields]})
        if self.secondaryFields:
            d.update({"secondaryFields": [f.json_dict() for f in self.secondaryFields]})
        if self.backFields:
            d.update({"backFields": [f.json_dict() for f in self.backFields]})
        if self.auxiliaryFields:
            d.update({"auxiliaryFields": [f.json_dict() for f in self.auxiliaryFields]})
        return d


class BoardingPass(PassInformation):

    def __init__(self, transitType=TransitType.AIR):
        super().__init__()
        self.transitType = transitType
        self.jsonname = "boardingPass"

    def json_dict(self):
        d = super().json_dict()
        d.update({"transitType": self.transitType})
        return d


class Coupon(PassInformation):

    def __init__(self):
        super().__init__()
        self.jsonname = "coupon"


class EventTicket(PassInformation):

    def __init__(self):
        super().__init__()
        self.jsonname = "eventTicket"


class Generic(PassInformation):

    def __init__(self):
        super().__init__()
        self.jsonname = "generic"


class StoreCard(PassInformation):
    jsonname = "storeCard"


class Pass(BaseModel):

    _files: dict[str, bytes] = {}
    _hashes: dict[str, str] = {}

    # Standard Keys

    # Required. Team identifier of the organization that originated and
    # signed the pass, as issued by Apple.
    teamIdentifier: str
    # Required. Pass type identifier, as issued by Apple. The value must
    # correspond with your signing certificate. Used for grouping.
    passTypeIdentifier: str
    # Required. Display name of the organization that originated and
    # signed the pass.
    organizationName: str
    # Required. Serial number that uniquely identifies the pass.
    serialNumber: str
    # Required. Brief description of the pass, used by the iOS
    # accessibility technologies.
    description: str
    # Required. Version of the file format. The value must be 1.
    formatVersion: int = 1

    # Visual Appearance Keys
    backgroundColor: str | None = None  # Optional. Background color of the pass
    foregroundColor: str | None = None  # Optional. Foreground color of the pass,
    labelColor: str | None = None  # Optional. Color of the label text
    logoText: str | None = None  # Optional. Text displayed next to the logo
    barcode: Barcode | None = (
        None  # Optional. Information specific to barcodes.  This is deprecated and can only be set to original barcode formats.
    )
    barcodes: list[Barcode] | None = None  # Optional.  All supported barcodes
    # Optional. If true, the strip image is displayed
    suppressStripShine: bool = False

    # Web Service Keys

    # Optional. If present, authenticationToken must be supplied
    webServiceURL: str | None = None
    # The authentication token to use with the web service
    authenticationToken: str | None = None

    # Relevance Keys

    # Optional. Locations where the pass is relevant.
    # For example, the location of your store.
    locations = None
    # Optional. IBeacons data
    ibeacons: list[IBeacon] | None = None
    # Optional. Date and time when the pass becomes relevant
    relevantDate = None

    # Optional. A list of iTunes Store item identifiers for
    # the associated apps.
    associatedStoreIdentifiers = None
    appLaunchURL = None
    # Optional. Additional hidden data in json for the passbook
    userInfo = None

    expirationDate = None
    voided = None

    passInformation: PassInformation

    class Config:
        arbitrary_types_allowed = True

    # Adds file to the file array
    def addFile(self, name, fd):
        self._files[name] = fd.read()

    # Creates the actual .pkpass file
    def create(self, certificate, key, wwdr_certificate, password, zip_file=None):
        pass_json = self._createPassJson()
        manifest = self._createManifest(pass_json)
        signature = self._createSignatureCrypto(
            manifest, certificate, key, wwdr_certificate, password
        )
        if not zip_file:
            zip_file = BytesIO()
        self._createZip(pass_json, manifest, signature, zip_file=zip_file)
        return zip_file

    def _createPassJson(self):
        return json.dumps(self, default=PassHandler)

    def _createManifest(self, pass_json):
        """
        Creates the hashes for all the files included in the pass file.
        """
        self._hashes["pass.json"] = hashlib.sha1(pass_json.encode("utf-8")).hexdigest()
        for filename, filedata in self._files.items():
            self._hashes[filename] = hashlib.sha1(filedata).hexdigest()
        return json.dumps(self._hashes)

    def _createSignatureCrypto(
        self, manifest, certificate, key, wwdr_certificate, password
    ):
        """
        Creates a signature (DER encoded) of the manifest.
        Rewritten to use cryptography library instead of M2Crypto
        The manifest is the file
        containing a list of files included in the pass file (and their hashes).
        """
        cert = x509.load_pem_x509_certificate(self._readFileBytes(certificate))
        priv_key = serialization.load_pem_private_key(
            self._readFileBytes(key), password=password.encode("UTF-8")
        )
        wwdr_cert = x509.load_pem_x509_certificate(
            self._readFileBytes(wwdr_certificate)
        )

        options = [pkcs7.PKCS7Options.DetachedSignature]
        return (
            pkcs7.PKCS7SignatureBuilder()
            .set_data(manifest.encode("UTF-8"))
            .add_signer(cert, priv_key, hashes.SHA1())
            .add_certificate(wwdr_cert)
            .sign(serialization.Encoding.DER, options)
        )

    # Creates .pkpass (zip archive)
    def _createZip(self, pass_json, manifest, signature, zip_file=None):
        zf = zipfile.ZipFile(zip_file or "pass.pkpass", "w")
        zf.writestr("signature", signature)
        zf.writestr("manifest.json", manifest)
        zf.writestr("pass.json", pass_json)
        for filename, filedata in self._files.items():
            zf.writestr(filename, filedata)
        zf.close()

    def json_dict(self):
        d = {
            "description": self.description,
            "formatVersion": self.formatVersion,
            "organizationName": self.organizationName,
            "passTypeIdentifier": self.passTypeIdentifier,
            "serialNumber": self.serialNumber,
            "teamIdentifier": self.teamIdentifier,
            "suppressStripShine": self.suppressStripShine,
            self.passInformation.jsonname: self.passInformation.json_dict(),
        }
        # barcodes have 2 fields, 'barcode' is legacy so limit it to the legacy formats, 'barcodes' supports all
        if self.barcode:
            original_formats = [
                BarcodeFormat.PDF417,
                BarcodeFormat.QR,
                BarcodeFormat.AZTEC,
            ]
            legacyBarcode = self.barcode
            newBarcodes = [self.barcode.json_dict()]
            if self.barcode.format not in original_formats:
                legacyBarcode = Barcode(
                    self.barcode.message, BarcodeFormat.PDF417, self.barcode.altText
                )
            d.barcode = legacyBarcode
            d.barcodes = newBarcodes

        if self.relevantDate:
            d.relevantDate = self.relevantDate
        if self.backgroundColor:
            d.backgroundColor = self.backgroundColor
        if self.foregroundColor:
            d.foregroundColor = self.foregroundColor
        if self.labelColor:
            d.labelColor = self.labelColor
        if self.logoText:
            d.logoText = self.logoText
        if self.locations:
            d.locations = self.locations
        if self.ibeacons:
            d.ibeacons = self.ibeacons
        if self.userInfo:
            d.userInfo = self.userInfo
        if self.associatedStoreIdentifiers:
            d.associatedStoreIdentifiers = self.associatedStoreIdentifiers
        if self.appLaunchURL:
            d.appLaunchURL = self.appLaunchURL
        if self.expirationDate:
            d.expirationDate = self.expirationDate
        if self.voided:
            d.voided = True
        if self.webServiceURL:
            d.update(
                {
                    "webServiceURL": self.webServiceURL,
                    "authenticationToken": self.authenticationToken,
                }
            )
        return d


def PassHandler(obj):
    if hasattr(obj, "json_dict"):
        return obj.json_dict()

    # For Decimal latitude and logitude etc.
    return str(obj) if isinstance(obj, decimal.Decimal) else obj
