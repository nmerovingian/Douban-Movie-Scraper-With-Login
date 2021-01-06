import requests
import csv
from fake_useragent import UserAgent
from lxml import etree
import os
import re
import time
import datetime
from hashlib import md5
import pickle
from concurrent.futures import ThreadPoolExecutor
ua = UserAgent()
headers = {'User-Agent' : ua.random}



#md5_set = set()




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

def parse_comments(url,session,film,start,stop,max_comments,md5_set):
    start_date = datetime.datetime.now().strftime(r'%Y-%m-%d')

    if stop> max_comments:
        print('The maximum comments available is:{}'.format(max_comments))
        os.abort()
    with open("{}_new_comments {}.csv".format(film[0],start_date),mode='a',newline='',encoding='UTF-8-sig') as f:
        writer = csv.writer(f)
        for index in range(start,stop,20):
            print('parsing comments {}'.format(index))
            comment_page = '{}/comments?start={}&limit=20&status=P&sort=time'.format(url,index)

            headers = {'User-Agent' : ua.random}
            try:
                response = session.get(comment_page,headers=headers)
            except:
                return
            
            
            
            
            s=etree.HTML(response.text)
            user_names = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/a/text()')
            comments = s.xpath('//*[@id="comments"]/div/div[2]/p/span/text()')
            dates = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[3]/@title')
            #dates = [date.strip() for date in dates]
            scores = s.xpath('//*[@id="comments"]/div/div[2]/h3/span[2]/span[2]/@class')
            scores = [score.replace('allstar','') for score in scores]
            scores = [score.replace(' rating','')for score in scores]
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

            if len(user_names) and len(user_names)==len(comments):
            
                for i in range(len(user_names)):
                    user_names[i]
                    comments[i]
                    #print(len(dates))
                    dates[i]
                    scores[i]
                    upvotes[i]
                    gathered_info = user_names[i]+user_names[i]+watched_already[i]+comments[i]+dates[i]+scores[i]+upvotes[i]
                    digest_algorithm = md5()
                    digest_algorithm.update(gathered_info.encode())
                    hexcode = digest_algorithm.hexdigest()
                    if hexcode not in md5_set:
                        writer.writerow([datetime.datetime.now(),user_names[i],watched_already[i],comments[i],dates[i],scores[i],upvotes[i]])
                        md5_set.add(hexcode)
                        print(film,'New comments Found!')

                with open('{}.pkl'.format(film),'wb') as f :
                    pickle.dump(md5_set,f)

            else:
                print(film,'Blocked! ')
                time.sleep(10)

            
            
            #Sleep two seconds for every request to prevent getting banned by the server. 
            
            
            time.sleep(5)


def parse_movie(home_page,parsing_interval):

    session = requests.Session()


    film,director,actor,length,total_review_number = parse_homepage(home_page,session)

    if os.path.exists('{}.pkl'.format(film)):

        with open('{}.pkl'.format(film),'rb') as f :
            md5_set = pickle.load(f)

    else:
        md5_set = set()
        with open('{}.pkl'.format(film),'wb') as f :
            pickle.dump(md5_set,f)



    #Parse the home page

    """
    with open('{}_new_comments {}.csv'.format(film[0],start_date),mode='w',newline='',encoding='UTF-8-sig') as f:
        writer = csv.writer(f)
        writer.writerows([film,director,actor,length])
        writer.writerow(['\n'])
        writer.writerow(['Parsing Time','UserName','Watched Already','Comments','Dates','Review_Score','Upvote'])"""






    stop = 81 # only a maximum of 100 is shown by Douban
    parse_comments(home_page,session,film=film,start=0,stop=stop,max_comments=total_review_number,md5_set=md5_set)

    #stop = 21 #Now only parse the first page of new comments

    while(True):

        parse_comments(home_page,session,film,start=0,stop=stop,max_comments=total_review_number,md5_set=md5_set)

        time.sleep(parsing_interval)


def foo(movie, parsing_interval):
    print(movie,parsing_interval)


if __name__ == "__main__":
    start_date = datetime.datetime.now().strftime(r'%Y-%m-%d')

    home_pages = set()



    """
    while True:
        home_page = input('Paste the url of the home page here. Enter one url at a time.\nPress ENTER to finish.\n')
        if len(home_page)>0:
            home_pages.add(home_page)
        else:
            break"""

    home_pages = {'https://movie.douban.com/subject/26673282/', 'https://movie.douban.com/subject/30284141/'}

        
    print(home_pages)





    parsing_interval = int(input('Parsing interval in minutes\n'))*60


    with ThreadPoolExecutor() as executor:

        executor.map(parse_movie,list(home_pages),[parsing_interval]*len(home_pages))

