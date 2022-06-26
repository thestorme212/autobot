from locale import currency
from freelancersdk.resources.projects import place_project_bid
from freelancersdk.session import Session
from freelancersdk.resources.users \
    import get_self_user_id
from freelancersdk.resources.projects.projects import (
    get_projects, get_project_by_id
)
from freelancersdk.resources.projects.helpers import (
    create_get_projects_object, create_get_projects_project_details_object,
    create_get_projects_user_details_object
)
from freelancersdk.exceptions import BidNotPlacedException
from freelancersdk.resources.projects.exceptions import \
    ProjectsNotFoundException
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_user_details_object,
    create_get_projects_project_details_object,
)
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.exceptions import \
    ProjectsNotFoundException

from freelancersdk.resources.users.users import get_self
from freelancersdk.resources.users.exceptions import \
    SelfNotRetrievedException
from freelancersdk.resources.users.helpers import (
    create_get_users_details_object
)

from freelancersdk.resources.projects.projects import get_bids
from freelancersdk.resources.projects.exceptions import \
    BidsNotFoundException

import os
import json

import time
import requests

freelancer_oauth_token = "72tC2owzEZOzbhqX3OXzojqM11uOzs"
chat_id = "@postbotsolix_bot"

BOT_TOKEN = "5528889143:AAEndA4v8AichxLz8tjqFTdj_KFNxtMMs_Q"
base_url = "https://api.telegram.org/bot" + BOT_TOKEN
offset = 0

time_interval = 60  # (in seconds) Specify the frequency of code execution

url = os.environ.get('FLN_URL')
bid_description = '''
★★★ Scrapping / Python / Selenium Expert ★★★ 6+ Years of Experience ★★★
Please allow me to generate a few sample entries in order to gain your trust and satisfaction. I have reviewed your project requirements closely and can help you with this. We can discuss also the complexity of the project so I can provide you with a realistic ETA and feel free to contact me through chat to talk about your project in more detail. 
I have extensive knowledge of web scrapping with Python,scrapy, BeautifulSoup, Selenium. My extensive experience with web scraping using IP proxy rotation, multi thread and Bypassing captcha. You can see my past work on freelancer and on github.
I'll be glad to discuss project before start so let's chat.
Thanks for your consideration.
Best Regards,
Ritesh
'''


def sample_search_projects():
    session = Session(oauth_token=freelancer_oauth_token, url=url)

    query = 'scraper scraping scrape'
    search_filter = create_search_projects_filter(
        sort_field='time_updated',
        min_avg_price=100,
        project_types='fixed',
        or_search_query=True,
    )

    try:
        p = search_projects(
            session,
            query=query,
            search_filter=search_filter
        )

    except ProjectsNotFoundException as e:
        print('Error message: {}'.format(e.message))
        print('Server response: {}'.format(e.error_code))
        return None
    else:
        return p


while True:
    p = sample_search_projects()
    time.sleep(time_interval)

    if p:

        for x in p.get('projects'):
            title = x.get('title')

            project_id = x.get('id')

            session = Session(oauth_token=freelancer_oauth_token, url=url)
            my_user_id = get_self_user_id(session)

            get_bids_data = {
                'project_ids': [project_id],
                'limit': 25,
                'offset': 0,
            }

            # bid amount = (Project MAX Budget - Avergage Bid AMount)/2 + Avergage Bid Amount
            # You can write your own formula
            amount = int((x.get('budget').get('maximum') - x.get('bid_stats').get('bid_avg')) / 2) + x.get(
                'bid_stats').get('bid_avg')

            try:
                bid = get_bids(session, **get_bids_data)
                if bid and x.get('status') == 'active' and (
                        x.get('currency').get('code') == 'USD' or x.get('currency').get('code') == 'AUD'):
                    print('Found bids: {}'.format(len(bid['bids'])))
                    if len(bid['bids']) < 20:
                        bid_data = {
                            'project_id': int(project_id),
                            'bidder_id': my_user_id,
                            'amount': amount - 75,
                            'period': 7,
                            'milestone_percentage': 20,
                            'description': bid_description,
                        }

                        print(bid_data)
                        print('https://www.freelancer.com/projects/' + x.get('seo_url'))
                        message = 'https://www.freelancer.com/projects/' + x.get('seo_url')
                        b = place_project_bid(session, **bid_data)
                        if b:
                            print('*********************')
                            print(("Bid placed: %s" % b))
                            parameters = {
                                "chat_id": chat_id,
                                "text": message,
                            }
                            resp = requests.get(base_url + "/sendMessage", data=parameters)



            except BidsNotFoundException as e:
                print('Error message: {}'.format(e.message))
                print('Server response: {}'.format(e.error_code))
                continue
            except:
                continue