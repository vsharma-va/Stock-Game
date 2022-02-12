from pathlib import Path
import csv


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
            if filePath.is_file():
                data = self.getPastPurchases()
                if purchaseDetails[0] in data[0]:
                    idx = data[0].index(purchaseDetails[0])
                    data[0][idx] = purchaseDetails[0]
                    quantity = int(data[1][idx])
                    quantity += int(purchaseDetails[1])
                    amount = float(data[2][idx])
                    amount += float(purchaseDetails[2])
                    data[1][idx] = quantity
                    data[2][idx] = amount
                    print(idx)
                    print(data)
                    transform = True
                else:
                    data[0].append(purchaseDetails[0])
                    data[1].append(purchaseDetails[1])
                    data[2].append(purchaseDetails[2])
                    transform = False

                with open(filePath, 'w', newline='', encoding='utf-8') as file_purchase_append:
                    writer = csv.writer(file_purchase_append)
                    writer.writerow(["Company Name", "Quantity", "Cost"])
                    if transform:
                        for i in range(len(data[0])):
                            writer.writerow([data[0][i], data[1][i], data[2][i]])
                    else:
                        writer.writerow(purchaseDetails)
            else:
                with open(filePath, 'w', newline='', encoding='utf-8') as file_purchase_write:
                    writer = csv.writer(file_purchase_write)
                    writer.writerow(["Company Name", "Quantity", "Cost"])
                    writer.writerow(purchaseDetails)
        elif purpose.lower() == "sold":
            filePath = Path(f"../../Data/UserInformation/purchase_history.csv")
            data = self.getPastPurchases()
            idx = data[0].index(purchaseDetails[0])
            newQuantity = int(data[1][idx]) - int(purchaseDetails[1])
            print(purchaseDetails[1])
            newAmount = float(data[2][idx]) - float(purchaseDetails[2])
            if newQuantity == 0:
                data[0].pop(idx)
                data[1].pop(idx)
                data[2].pop(idx)
            else:
                data[1][idx] = newQuantity
                data[2][idx] = newAmount
            with open(filePath, 'w', encoding='utf-8', newline='') as file_sold_write:
                writer = csv.writer(file_sold_write)
                for i in range(len(data[0])):
                    writer.writerow(["Company Name", "Quantity", "Cost"])
                    writer.writerow([data[0][i], data[1][i], data[2][i]])

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
