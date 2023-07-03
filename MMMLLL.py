import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# 우리의 프로젝트를 함꼐할 특이점장전 클래스를 생성하자!!!!!!!!1
class Singularity:

    # 생성자 함수
    def __init__(self, _file_list=None, _date_list=None):
        self.file_list = _file_list
        self.date_list = _date_list
        # (self, _file_list, _df=None, _date_list=None, _col_list=None)
        # self.df = _df
        # self.date_list = _date_list
        # self.col_list = _col_list


    ## Kospi200 종목의 월별 개별 팩터데이터를 데이터 프레임의 형태로 받아오자
    def get_month_df(self, df):

        dataframes = []
        for k, flie in enumerate(self.file_list):

            code1 = pd.read_excel(f'./KOSPI200_종목코드/{flie}')    # 375500 000810
            code1.columns = code1.iloc[2,:].values
            code1 = code1.iloc[3:,:]
            # data6['시점'] = data6['시점'].astype(str)
            code1.set_index(code1.columns[0], inplace=True)


            code1.index = pd.to_datetime(code1.index, format='%Y.%m.%d')
            code1.index = pd.to_datetime(code1.index.date)
            code1.sort_index(ascending=True, inplace=True)
            code1.drop('종가(원)', axis=1, inplace=True)

            code_col_list = code1.columns

            for i in range(len(code_col_list)):
                globals()[f"value_list{i+1}"] = []
            date = datetime.strptime('2007-03-01', '%Y-%m-%d') 
            code_col_list = code1.columns

            date_list2 = []
            for i in range(64):

                for j, col in enumerate (code_col_list):
                    temp = code1[((code1.index.month == date.month)|(code1.index.month == date.month-1)|(code1.index.month == date.month-2))& (code1.index.year == date.year)][col]

                    temp_nan_num = temp.isna().sum()
                    temp = temp.fillna(0)

                    temp_avg = temp.values.astype(float).sum()/(len(temp) - temp_nan_num) 
                    globals()[f"value_list{j+1}"].append(temp_avg)

                date_list2.append(date)
                date = date+relativedelta(months=3)
                
            my_dict = {}
            for i in range(len(code_col_list)):
                my_dict[code_col_list[i]] = globals()[f"value_list{i+1}"]

            df_new = pd.DataFrame(my_dict, index=date_list2)

            df_code = df.loc[df['거래소코드']== flie.replace('.xlsx','')]
            df_code = df_code.reindex(date_list2)
            df_code.drop(['회사명', '거래소코드'], axis=1, inplace=True)
            # df_code.drop(['회사명', '거래소코드', 'PER', 'PBR', 'PCR'], axis=1, inplace=True)

            df_new2 = pd.concat([df_new, df_code], axis=1)
            df_new2 = df_new2.replace(0, np.nan)

            # ## 선형 보간법 ###
            # col_list = df_new2.columns
            # for col in col_list:
            #     df_new2[col].interpolate(method='linear', inplace=True)
            # #################
            
            globals()[f"temp{k+1}"] = df_new2

            dataframes.append(globals()[f"temp{k+1}"])

            print(f'{k}번째 읽어옴')

        return dataframes


    
    # 2007/06부터 2022/12까지 각 기간별로 col_list = ['정상영업이익증가율', '순이익증가율', '1주당순이익', '부채비율', '매출액정상영업이익률', '매출액증가율', 'PER', 'PBR', 'PCR']
    # 을 기준으로 long position, short position을 가지는 데이터들을 리스트에 형태로 저장해두었다.
    # self.long_list는 2007/06~2022/12에서의 col_list에 나온 각각의 기준별로 long position을 취할 종목들의 코드를 담았다.
    # self.short_list는 2007/06~2022/12에서의 col_list에 나온 각각의 기준별로 short position을 취할 종목들의 코드를 담았다.
    def long_short(self, dataframes):
        self.long_list = []
        self.short_list = []
        col_list = dataframes[0].columns

        for i in self.date_list:

            for k, col in enumerate(col_list):

                temp_list = []
                long_ll = []
                short_ll = []
                for j in range(len(dataframes)):
                    temp = dataframes[j][col][i]
                    temp_list.append(temp)
                
                temp_df = pd.DataFrame(temp_list)

                num = int(len(temp_df.dropna())/5)

                long_index = temp_df[0].sort_values(ascending=False)[0:num].index
                short_index = temp_df[0].sort_values(ascending=True)[0:num].index

                # temp_list = df_temp[j].sort_values(ascending=True)[0:short_num].index

                for idx in long_index:
                    long_ll.append(self.file_list[idx].replace('.xlsx',''))

                for idx in short_index:
                    short_ll.append(self.file_list[idx].replace('.xlsx',''))
            
                self.long_list.append(long_ll)
                self.short_list.append(short_ll)

        return self.long_list, self.short_list
    




    # 한 개별 팩터에 대한 사후수익률을 구하는 코드
    def get_posterior_rate(self, long_li, short_li, dfs):

        # self.rate_sum = []   # 1개월 단위로한 해당팩터기준 사후 수익률 데이터를 저장하기위한 변수
        # default_date = datetime.strptime('2007-07-01', '%Y-%m-%d')  # 초기 시간(2007년7월1일)

        long_rate_sum = []
        for i in range(len(long_li)):
            
            date = self.date_list[i]
            # 특정 기간에서 특정 팩터 기준으로 long칠 종목들
            long_tem = long_li[i]

            len_code = len(long_tem)

            # long_temp = []  ##
            # 상위 20% 데이터 롱치자
            long_temp_rate = 0
            for code_tem in long_tem:

                ind = self.file_list.index(code_tem+'.xlsx')
                temp = dfs[ind][((dfs[ind].index.month == date.month)|(dfs[ind].index.month == date.month-1)|(dfs[ind].index.month == date.month-2))& (dfs[ind].index.year == date.year)]['종가(원)']

                if temp.empty != True:
                    long_temp_rate = long_temp_rate + (temp[-1] - temp[0])/temp[0]
                    # long_temp.append(long_temp_rate)    ##
                else:
                    len_code = len_code -1 
            
            if len_code == 0:
                long_temp_rate = 0
            else:
                long_temp_rate = long_temp_rate/len_code

            long_rate_sum.append(long_temp_rate)
            # print(f'{i}번째 기간 읽어오기 완료')           

        short_rate_sum = []
        for i in range(len(short_li)):

            date = self.date_list[i]
            # 특정 기간에서 특정 팩터 기준으로 long칠 종목들
            short_tem = short_li[i]

            len_code = len(short_tem )

            short_temp_rate = 0
            # 상위 20% 데이터 롱치자
            for code_tem in short_tem:

                ind = self.file_list.index(code_tem+'.xlsx')
                temp = dfs[ind][((dfs[ind].index.month == date.month)|(dfs[ind].index.month == date.month-1)|(dfs[ind].index.month == date.month-2))& (dfs[ind].index.year == date.year)]['종가(원)']

                if temp.empty != True:
                    short_temp_rate = short_temp_rate + (temp[0] - temp[-1])/temp[0]
                    # long_temp.append(long_temp_rate)    ##
                else:
                    len_code = len_code -1 
            
            if len_code == 0:
                short_temp_rate = 0
            else:
                short_temp_rate = short_temp_rate/len_code

            
            short_rate_sum.append(short_temp_rate)


        # self.rate_sum = [a + b for a, b in zip(long_rate_sum, short_rate_sum)]
        
        return long_rate_sum, short_rate_sum
    



    
    # 거시변수 월 데이터 뽑기
    def get_month_data(self, df, col_name, set_col_name):

        date = datetime.strptime('2007-07-01', '%Y-%m-%d') 
        date_list2 = []
        for i in range(191):
            date_list2.append(date)
            date = date+relativedelta(months=1)

        year = 2007
        mon = 7
        value_list = []
        for j in range(191):
            temp = df[(df.index.month == mon)& (df.index.year == year)][col_name]

            temp_nan_num = temp.isna().sum()
            temp = temp.fillna(0)

            temp_avg = temp.values.sum()/(len(temp) - temp_nan_num)    #-temp_nan_num
            value_list.append(temp_avg)


            if mon == 12:
                year = year + 1
                mon = mon - 12
            
            mon = mon + 1
        
        df_selected = pd.DataFrame({
            set_col_name : value_list,
        }, index=date_list2)  # 시계열 데이터를 인덱스로 설정


        return df_selected