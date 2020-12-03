import requests
import csv
from fake_useragent import UserAgent
from lxml import etree
import os
import re
import time
ua = UserAgent()
headers = {'User-Agent' : ua.random}
from getpass import getpass


#home_page = "https://movie.douban.com/subject/20376577/"

#comment_page = 'https://movie.douban.com/subject/20376577/comments?start=0&limit=20&status=P&sort=new_score'



class DouBan(object):
    def __init__(self):
        self.login_url = 'https://accounts.douban.com/j/mobile/login/basic'
        self.headers = {
            "User-Agent": ua.safari  #"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
            ,#'cookie' : r'douban-fav-remind=1; _vwo_uuid_v2=D0EA24652E668F9059E333E4EBA7E0F0B|4113fd0dad106ebbed18eeb641145776; gr_user_id=c1273f03-0474-4cd8-9cd3-07849a4c6d05; bid=IM4E7IPnDN8; ll="108296"; viewed="34853568"; apiKey=; __utmz=30149280.1606972383.30.28.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmc=30149280; __utma=30149280.1529578497.1561719066.1606978260.1606981423.32; ap_v=0,6.0; _pk_ref.100001.2fad=%5B%22%22%2C%22%22%2C1606981444%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F20376577%2Fcomments%3Fstart%3D300%26limit%3D20%26status%3DP%26sort%3Dnew_score%22%5D; _pk_ses.100001.2fad=*; __utmt=1; _pk_id.100001.2fad=692b942217e57c96.1606981444.1.1606982044.1606981444.; user_data={%22area_code%22:%22+86%22%2C%22number%22:%2218580731201%22%2C%22code%22:%223195%22}; vtoken=undefined; last_login_way=phone; push_noty_num=0; push_doumail_num=0; douban-profile-remind=1; __utmv=30149280.19461; __utmb=30149280.7.10.1606981423; login_start_time=1606982465670'
        }
        self.login_data = {
            'ck': '',
            'name': input('User Name\n'),
            'password': getpass('Your Douban Password\n'),
            'remember': 'false',
            #'ticket': ''
        }
        self.session = requests.Session()
        self.login()

    def login(self):
        response = self.session.post(self.login_url, data=self.login_data, headers=self.headers)
        print(response.json())

    def get_html(self, url):
        return self.session.get(url, headers = self.headers)



def parse_homepage(url,session):
    data = session.get(url, headers=headers).text
    s=etree.HTML(data)

    film=s.xpath('//*[@id="content"]/h1/span[1]/text()')
    director=s.xpath('//*[@id="info"]/span[1]/span[2]/a/text()')
    actor=s.xpath('//*[@id="info"]/span[3]/span[2]/a/text()')
    length=s.xpath('//*[@id="info"]/span[13]/text()')
    total_review_number = s.xpath('//*[@id="comments-section"]/div[1]/h2/span/a/text()')
    pattern = re.compile(r'\d+')
    total_review_number = int(pattern.findall((str(total_review_number)).strip())[0])


    return(film,director,actor,length,total_review_number)


def parse_comments(url,session,start,stop,max_comments):


    if stop> max_comments:
        print(f'The maximum comments available is:{max_comments}')
        os.abort()
    with open(f'{film[0]}.csv',mode='a',newline='',encoding='UTF-8-sig') as f:
        writer = csv.writer(f)
        for index in range(start,stop,20):
            print(f'parsing comments {index}')
            comment_page = f'{url}/comments?start={index}&limit=20&status=P&sort=new_score'
            response = session.get(comment_page,headers=headers)
            
            
            
            
            s=etree.HTML(response.text)
            user_names = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/a/text()')
            comments = s.xpath('//*[@id="comments"]/div/div[2]/p/span/text()')
            dates = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[3]/@title')
            #dates = [date.strip() for date in dates]
            scores = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[2]/@class')
            upvotes = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[1]/span/text()')
            watched_already = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[1]/text()')

            dates_without_score = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[2]/@title')
            
            no_review_index = []
            for i,date in enumerate(dates_without_score):
                if date.startswith('2') or date.startswith('1'):
                    no_review_index.append(i)

            no_score_review_date = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[2]/text()')
            no_score_review_date = [date.strip() for date in no_score_review_date]

            if len(no_review_index):
                for i,value in enumerate(no_review_index):
                    dates.insert(value,no_score_review_date[i])


            #print(no_review_index)

            #print(len(user_names),len(comments),len(dates),len(scores),len(upvotes),len(watched_already))

            if len(user_names):
            
                for i in range(len(user_names)):
                    user_names[i]
                    comments[i]
                    #print(len(dates))
                    dates[i]
                    scores[i]
                    upvotes[i]
                    writer.writerow([user_names[i],watched_already[i],comments[i],dates[i],scores[i],upvotes[i]])
            else:
                print('Blocked! ')
                time.sleep(10)

            
            
            #Sleep two seconds for every request to prevent getting banned by the server. 
            
            
            time.sleep(5)
            






if __name__ == "__main__":
    douban = DouBan()
    douban.login()
    session = douban.session
    home_page = input('Paste the url of the home page here.\n')

    film,director,actor,length,total_review_number = parse_homepage(home_page,session)

    #Parse the home page 
    with open(f'{film[0]}.csv',mode='w',newline='',encoding='UTF-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows([film,director,actor,length])
        writer.writerow(['\n'])
        writer.writerow(['UserName','Watched Already','Comments','Dates','Review_Score','Upvote'])



    stop = int(input(f'How many comments do you want to parse? Maximum of {total_review_number}\n'))


    parse_comments(home_page,session,start=0,stop=stop,max_comments=total_review_number)



    
    
        

