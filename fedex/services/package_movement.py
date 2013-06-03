"""
Package Movement Information Service
====================================
This package contains classes to check service availability, route, and postal
codes. Defined by the PackageMovementInformationService WSDL file. 
"""
from .. base_service import FedexBaseService, FedexError

class FedexPostalCodeNotFound(FedexError):
    """
    Exception: Sent when the postalcode is missing.
    """
    pass

class FedexInvalidPostalCodeFormat(FedexError):
    """
    Exception: Sent when the postal code is invalid
    """
    pass

class PostalCodeInquiryRequest(FedexBaseService):
    """
    The postal code inquiry enables customers to validate postal codes
    and service commitments.
    """
    def __init__(self, config_obj,
                 wsdl_name='PackageMovementInformationService_v4.wsdl',
                 version_info=('4', '0', '0'), postal_code=None,
                 country_code=None, *args, **kwargs):
        """
        Sets up an inquiry request. The optional keyword args
        detailed on L{FedexBaseService} apply here as well.
        
        @type config_obj: L{FedexConfig}
        @param config_obj: A valid FedexConfig object

        @type wsdl_name: str
        @param wsdl_name: The name of the wsdl file.

        @type version_info: tuple
        @param version_info: Holds the major, intermediate, and minor components of the version as strings

        @param postal_code: a valid postal code
        @param country_code: ISO country code to which the postal code belongs to.
        """
        self._config_obj = config_obj
        
        # Holds version info for the VersionId SOAP object.
        self._version_info = {'service_id': 'pmis', 'major': version_info[0],
                              'intermediate': version_info[1],
                              'minor': version_info[2]}
        self.PostalCode = postal_code
        self.CountryCode = country_code
       
       
        # Call the parent FedexBaseService class for basic setup work.
        super(PostalCodeInquiryRequest, self).__init__(self._config_obj,
                                                       wsdl_name,
                                                       *args, **kwargs)
        

    def _check_response_for_request_errors(self):
        """
        Checks the response to see if there were any errors specific to
        this WSDL.
        """
        if self.response.HighestSeverity == "ERROR":
            for notification in self.response.Notifications:
                if notification.Severity == "ERROR":
                    if "Postal Code Not Found" in notification.Message:
                        raise FedexPostalCodeNotFound(notification.Code,
                                                         notification.Message)

                    elif "Invalid Postal Code Format" in self.response.Notifications:
                        raise FedexInvalidPostalCodeFormat(notification.Code,
                                                         notification.Message)
                    else:
                        raise FedexError(notification.Code,
                                         notification.Message)
                                         
    def _prepare_wsdl_objects(self):
        pass
 
        
    def _assemble_and_send_request(self):
        """
        Fires off the Fedex request.
        
        @warning: NEVER CALL THIS METHOD DIRECTLY. CALL send_request(), WHICH RESIDES
            ON FedexBaseService AND IS INHERITED.
        """
        client = self.client
        
       
        # We get an exception like this when specifying an IntegratorId:
        # suds.TypeNotFound: Type not found: 'IntegratorId'
        # Setting it to None does not seem to appease it.
        
        del self.ClientDetail.IntegratorId
        
        # Fire off the query.
        response = client.service.postalCodeInquiry(WebAuthenticationDetail=self.WebAuthenticationDetail,
                                        ClientDetail=self.ClientDetail,
                                        TransactionDetail=self.TransactionDetail,
                                        Version=self.VersionId,
                                        PostalCode = self.PostalCode,
                                        CountryCode = self.CountryCode)

        return response
        
