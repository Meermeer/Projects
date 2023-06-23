import pandas as pd
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 우리의 프로젝트를 함꼐할 특이점장전 클래스를 생성하자!!!!!!!!1
class Singularity:

    # 생성자 함수
    def __init__(self, _df=None, _date_list=None, _col_list=None):
        self.df = _df
        self.date_list = _date_list
        self.col_list = _col_list

    # 2007/6부터 2022/12까지 날짜 정보를 리스트의 형태로 뽑아오는 함수
    def getdate(self):
        self.date_list = []
        i = 7
        j = 6
        for p in range(32):
            if (i < 10) & (j < 12):
                temp = '200'+str(i) +'/0'+str(j)
                self.date_list.append(temp)
                j = j + 6

            elif (i < 10) & (j >= 12):
                temp = '200'+str(i) +'/'+str(j)
                self.date_list.append(temp)
                j = j - 6
                i = i + 1

            elif (i >= 10) & (j < 12):
                temp = '20'+str(i) +'/0'+str(j)
                self.date_list.append(temp)
                j = j + 6   

            else:
                temp = '20'+str(i) +'/'+str(j)
                self.date_list.append(temp)
                j = j - 6
                i = i + 1    
        return self.date_list
    
    # 2007/06부터 2022/12까지 각 기간별로 col_list = ['정상영업이익증가율', '순이익증가율', '1주당순이익', '부채비율', '매출액정상영업이익률', '매출액증가율', 'PER', 'PBR', 'PCR']
    # 을 기준으로 long position, short position을 가지는 데이터들을 리스트에 형태로 저장해두었다.
    # self.long_list는 2007/06~2022/12에서의 col_list에 나온 각각의 기준별로 long position을 취할 종목들의 코드를 담았다.
    # self.short_list는 2007/06~2022/12에서의 col_list에 나온 각각의 기준별로 short position을 취할 종목들의 코드를 담았다.
    def long_short(self):
        self.long_list = []
        self.short_list = []

        for i in self.date_list:

            df_temp = self.df.loc[self.df['회계년도']==i]    
            num = len(df_temp['거래소코드'])
            long_num = int(num/5)
            short_num = int(num/5)

            for j in self.col_list:

                long_index = df_temp[j].sort_values(ascending=False)[0:long_num].index
                short_index = df_temp[j].sort_values(ascending=True)[0:short_num].index

                long_temp_list = list(df_temp['거래소코드'][long_index])
                short_temp_list = list(df_temp['거래소코드'][short_index])

                self.long_list.append(long_temp_list)
                self.short_list.append(short_temp_list)  

        return self.long_list, self.short_list
    
    def get_posterior_rate(self, long_li, short_li):

        # 각 팩터별로 사후수익률을 구해보자
        self.rate_sum = []   # 1개월 단위로한 해당팩터기준 사후 수익률 데이터를 저장하기위한 변수

        default_date = datetime.strptime('2007-07-01', '%Y-%m-%d')  # 초기 시간(2007년7월1일)
        date = default_date 


        for i in range(len(long_li)):
            
            # 특정 기간에서 특정 팩터 기준으로 long치거나 short칠 종목
            long_tem = long_li[i]
            short_tem = short_li[i]

            # # 월 바뀌었으니 값 갱신해야져 ~~.
            # temp_31_long_list = [0,0,0,0,0,0]
            # temp_1_long_list = [0,0,0,0,0,0]
            # temp_31_short_list = [0,0,0,0,0,0]
            # temp_1_short_list = [0,0,0,0,0,0]

            # 상위 20% 데이터 롱치자
            temp_rate = 0
            for k in long_tem:
                    
                temp_lastday = date+relativedelta(months=6)-timedelta(days=1)
                temp = fdr.DataReader(k, date, temp_lastday)

                temp_long_last_sum = 0
                temp_long_first_sum = 0

                if temp.empty != True:
                    # unique_num = len((temp.index.month).unique())
                    temp_len = len(temp['Close'])
                    temp_long_last_sum = temp_long_last_sum + temp['Close'].iloc[temp_len-1]     # 월 마지막날의 종가
                    temp_long_first_sum = temp_long_first_sum + temp['Close'].iloc[0]    # 월 시작일의 종가

                    temp_rate = temp_rate + (temp_long_last_sum - temp_long_first_sum)/temp_long_first_sum
                    # temp_long_rate.append(temp_rate) 
                    # for j in range(6, 6-unique_num, -1):
                    #     # 상장 안되서 데이터가 없으면 패스함.
                    #     last_month = temp.index.month[-1]
                    #     temp_data = temp[temp.index.month == (last_month-(6-j))]

                    #     temp_len = len(temp_data['Close'])
                    #     temp_31_long_list[j-1] = temp_31_long_list[j-1] + temp_data['Close'].iloc[temp_len-1]     # 월 마지막날의 종가
                    #     temp_1_long_list[j-1] = temp_1_long_list[j-1] + temp_data['Close'].iloc[0]                # 월 시작일의 종가
                

            # 하위 20% 데이터 숏치자
            temp_rate2 = 0
            for k_ in short_tem:
                    
                temp_lastday2 = date+relativedelta(months=6)-timedelta(days=1)
                temp2 = fdr.DataReader(k_, date, temp_lastday2)

                temp_short_last_sum = 0
                temp_short_first_sum = 0

                if temp2.empty != True:
                    temp_len = len(temp2['Close'])
                    temp_short_last_sum  = temp_short_last_sum  + temp2['Close'].iloc[temp_len-1]     # 월 마지막날의 종가
                    temp_short_first_sum = temp_short_first_sum + temp2['Close'].iloc[0]    # 월 시작일의 종가

                    temp_rate2 = temp_rate2 + (temp_short_first_sum  - temp_short_last_sum)/temp_short_first_sum

            temp_rate = temp_rate/len(long_tem)
            temp_rate2 = temp_rate2/len(short_tem)
            self.rate_sum.append(temp_rate+temp_rate2)
            # temp_short_rate.append(temp_rate2)

                    # unique_num2 = len((temp2.index.month).unique())
                    # for j in range(6, 6-unique_num2, -1):
                    #     # 상장 안되서 데이터가 없으면 패스함.
                    #     last_month2 = temp2.index.month[-1]
                    #     temp_data2 = temp2[temp2.index.month == (last_month2-(6-j))]

                    #     temp_len2 = len(temp_data2['Close'])
                    #     temp_31_short_list[j-1] = temp_31_short_list[j-1] + temp_data2['Close'].iloc[temp_len2-1]     # 월 마지막날의 종가
                    #     temp_1_short_list[j-1] = temp_1_short_list[j-1] + temp_data2['Close'].iloc[0]                # 월 시작일의 종가

                    #     # temp_short_31sum = temp_short_31sum + temp_data2['Close'].iloc[temp_len2-1]     # 월 마지막날의 종가
                    #     # temp_short_1sum = temp_short_1sum + temp_data2['Close'].iloc[0]                # 월 시작일의 종가

            # 롱,숏친거 총 수익률을 구하자
            # for m in range(6):
            #     temp_rate = (temp_31_long_list[m] - temp_31_short_list[m] - temp_1_long_list[m] + temp_1_short_list[m])/(temp_1_long_list[m]-temp_1_short_list[m])
            #     self.rate_sum.append(temp_rate)                              

            # 너무 오래걸려... 중간에 잘 되가는지나 함 보자
            print(f'{i}번째 기간 읽어오기 완료')           
            date = date + relativedelta(months=6)   # 6개월 경과
        
        return self.rate_sum
    
    # 거시변수 월 데이터 뽑기
    def get_month_data(self, df, col_name, set_col_name):

        date = datetime.strptime('2007-07-01', '%Y-%m-%d') 
        date_list = []
        for i in range(191):
            date_list.append(date)
            date = date+relativedelta(months=1)

        year = 2007
        mon = 7
        value_list = []
        for j in range(191):
            temp = df[(df.index.month == mon)& (df.index.year == year)][col_name]
            temp_avg = temp.values.sum()/len(temp)
            value_list.append(temp_avg)

            if mon == 12:
                year = year + 1
                mon = mon - 12
            
            mon = mon + 1
        
        df_selected = pd.DataFrame({
            set_col_name : value_list,
        }, index=date_list)  # 시계열 데이터를 인덱스로 설정

        return df_selected