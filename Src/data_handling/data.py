import os
from pathlib import Path
import csv
import pandas
import pandas as pd


class Data:
    def saveUserInformation(self, purpose: str, currentBalance: str='', purchaseDetails: list=[]):
        if purpose.lower() == "exit":
            filePath = Path(f"../../Data/UserInformation/balance.csv")
            if filePath.is_file():
                with open(filePath, 'w', newline='', encoding='utf-8') as file_balance:
                    writer = csv.writer(file_balance)
                    writer.writerow([currentBalance])
        elif purpose.lower() == "bought":
            filePath = Path(f"../../Data/UserInformation/purchase_history.csv")
            if filePath.is_file() and os.path.getsize(filePath) > 0:
                df = pandas.read_csv(filePath)
                found = df[df["Company Name"].str.contains(f"{purchaseDetails[0]}")]
                if len(found) > 0:
                    df.loc[df["Company Name"] == purchaseDetails[0], 'Quantity'] = \
                        int(df.loc[df["Company Name"] == purchaseDetails[0], 'Quantity']) + int(purchaseDetails[1])
                    df.loc[df["Company Name"] == purchaseDetails[0], 'Cost'] = \
                        float(df.loc[df["Company Name"] == purchaseDetails[0], 'Cost']) + float(purchaseDetails[2])

                    df.to_csv(filePath, index=False)

                elif len(found) == 0:
                    df.loc[len(df)] = purchaseDetails
                    print(df)
                    df.to_csv(filePath, mode='w+', index=False)
            else:
                df = pd.DataFrame([purchaseDetails], columns=["Company Name", "Quantity", "Cost"])
                df.to_csv(filePath)
        elif purpose.lower() == "sold":
            filePath = Path(f"../../Data/UserInformation/purchase_history.csv")
            df = pd.read_csv(filePath)
            df.loc[df["Company Name"] == purchaseDetails[0], 'Quantity'] = \
                int(df.loc[df["Company Name"] == purchaseDetails[0], 'Quantity']) - int(purchaseDetails[1])
            df.loc[df["Company Name"] == purchaseDetails[0], 'Cost'] = \
                float(df.loc[df["Company Name"] == purchaseDetails[0], 'Cost']) - float(purchaseDetails[2])

            df.drop(df[df.Quantity <= 0].index, inplace=True)

            df.to_csv(filePath, index=False)

    def getDataLiveGraph(self, item) -> list:
        with open(item[0], 'r', encoding='utf-8') as file_read:
            data = file_read.readlines()
        time_stamp = []
        price = []
        data.pop(0)
        for i in data:
            time_stamp.append(i.replace('\n', '').split(",")[0])
            price.append(float(i.replace('\n', '').split(",")[1]))
        return [time_stamp, price]

    def getUserBalance(self) -> list[bool, str]:
        path = Path("../../Data/UserInformation/balance.csv")
        if path.is_file():
            with open("../../Data/UserInformation/balance.csv", 'r', encoding='utf-8') as file_read:
                balance = file_read.readlines()
            file_read.close()
            print(balance)
            return [True, balance[0].strip('\n')]
        else:
            return [False, 0]

    def getPastPurchases(self) -> list[list[str], list[str], list[str]]:
        path = Path("../../Data/UserInformation/purchase_history.csv")
        if path.is_file():
            with open("../../Data/UserInformation/purchase_history.csv", 'r', encoding='utf-8') as file_read:
                data = file_read.readlines()
            try:
                data.pop(0)
            except IndexError:
                return[[], [], []]
            companyName = []
            quantity = []
            amount = []
            for i in data:
                y = i.split(',')
                companyName.append(y[0])
                quantity.append(y[1])
                amount.append(y[2].strip('\n'))

            return [companyName, quantity, amount]

        else:
            return [[], [], []]
