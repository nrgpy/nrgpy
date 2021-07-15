from auth import cloud_api, sites_url
import requests

class sites(cloud_api):
    
    def __init__(self, client_id, client_secret):
        
        super().__init__(client_id, client_secret)
    
        self.client_id = client_id
        self.client_secret = client_secret
        
        self.get_sites()
        
    def get_sites(self):
        self.headers = {"Authorization": "Bearer " + self.session_token,
                        }

        self.resp = requests.get(url=sites_url, headers=self.headers)
        
        self.sites_list = self.resp.json()['sites']
        
    def get_siteid(self, site='', logger_sn=''):
        if site and logger_sn:
            matching_sites = [site_dict for site_dict in self.sites_list if
             site_dict['siteNumber']==site and site_dict['loggerSerialNumber']==logger_sn]
            
            if len(matching_sites)==1:
                return matching_sites[0]['siteId']
            
            else:
                print("No site matches this site number and logger serial number. " +
                      "Confirm that you have entered the values correctly " +
                      "and that you have access to this site.")

        elif site:
            matching_sites = [site_dict for site_dict in self.sites_list if
             site_dict['siteNumber']==site]
            
            if len(matching_sites)>1:
                print("There is more than one site with that site number. " +
                      "Please use the logger serial number.")
                return None
            
            elif len(matching_sites)==1:
                return matching_sites[0]['siteId']

            else:
                print("No site matches this site number. " +
                      "Confirm that you have entered the value correctly " +
                      "and that you have access to this site.")

        elif logger_sn:
            matching_sites = [site_dict for site_dict in self.sites_list if
             site_dict['loggerSerialNumber']==logger_sn]
            
            if len(matching_sites)>1:
                print("There is more than one site with that logger serial number. " +
                      "Please use the site number.")
                return None
            
            elif len(matching_sites)==1:
                return matching_sites[0]['siteId']

            else:
                print("No site matches this logger serial number. " +
                      "Confirm that you have entered the value correctly " +
                      "and that you have access to this site.")
            