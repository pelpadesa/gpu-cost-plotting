import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import datetime
from plotly.subplots import make_subplots

color_map = {
    "RTX 4090": ("#6A2FCE", "#6BA000"),
    "RX 7900 XTX": ("#6A2FCE", "red"),
    "RX 6950 XT": ("#6A2FCE", "red"),
    "RTX 4080": ("#6A2FCE", "#6BA000"),
    "RX 6900 XT": ("#6A2FCE", "red"),
    "RX 7900 XT": ("#6A2FCE", "red"),
    "RTX 3090 Ti": ("#6A2FCE", "#6BA000"),
    "RTX 4070 Ti": ("#6A2FCE", "#6BA000"),
    "RX 6800 XT": ("#6A2FCE", "red"),
    "RTX 3090": ("#6A2FCE", "#6BA000"),
    "RTX 3080 Ti": ("#6A2FCE", "#6BA000"),
    "RTX 3080 12GB": ("#6A2FCE", "#6BA000"),
    "RTX 3080": ("#6A2FCE", "#6BA000"),
    "RX 6800": ("#6A2FCE", "red"),
    "RTX 3070 Ti": ("#6A2FCE", "#6BA000"),
    "RX 6750 XT": ("#6A2FCE", "red"),
    "RX 6700 XT": ("#6A2FCE", "red"),
    "RTX 3070": ("#6A2FCE", "#6BA000"),
    "RX 6700 10GB": ("#6A2FCE", "red"),
    "RX 6650 XT": ("#6A2FCE", "red"),
    "RTX 3050": ("#6A2FCE", "#6BA000"),
    "RTX 3060 Ti": ("#6A2FCE", "#6BA000"),
    "RX 6600": ("#6A2FCE", "red"),
    "RX 6600 XT": ("#6A2FCE", "red"),
    "RTX 3060": ("#6A2FCE", "#6BA000"),
    "Arc A770": ("#6A2FCE", "#2373CE"),
    "Arc A750": ("#6A2FCE", "#2373CE"),
    "Arc A380": ("#6A2FCE", "#2373CE")
}

class GPU:
    def __init__(self, name, fhdUltra, fhdMedium, qhdUltra, fourkUltra) -> None:
        for phrase in ["Intel ", "GeForce ", "Radeon ", " 16GB"]:
            if phrase in name:
                name = name.replace(phrase, "")
                if name == "VII":
                    name = "Radeon VII"
        self.Name = name
        self.fhdUltra = self.CleanData(fhdUltra)
        self.fhdMedium = self.CleanData(fhdMedium)
        self.qhdUltra = self.CleanData(qhdUltra)
        self.fourkUltra = self.CleanData(fourkUltra)

    def CleanData(self, value):
        if isinstance(value, float):
            return value
        value_ = ""
        for char in value:
            if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]:
                value_ += char
        try: 
            return float(value_)
        except:
            return 0.00
            
def LoadGPUs(pricing_data_csv: str):
    soup = BeautifulSoup(requests.get("https://www.tomshardware.com/reviews/gpu-hierarchy,4388.html").text, 'lxml')

    table = soup.select_one("#slice-container-table-7 > div.table__container > table")
    gpus = []
    for row in table.findAll("tr")[1:]:
        row_data = row.select("td")
        # [td td td td]
        gpu = GPU(
            name = row_data[0].text.replace(" (opens in new tab)", ""),
            fhdUltra = row_data[1].text.split("(")[1] if "fps" in row_data[1].text else 0.00,
            fhdMedium = row_data[2].text.split("(")[1] if "fps" in row_data[2].text else 0.00,
            qhdUltra = row_data[3].text.split("(")[1] if "fps" in row_data[3].text else 0.00,
            fourkUltra = row_data[4].text.split("(")[1] if "fps" in row_data[4].text else 0.00
        )
        if gpu.Name is None:
            continue

        gpus.append(gpu)
    priceData = LoadPrices(pricing_data_csv)
    gpus_ = []
    for gpu in gpus:
        if priceData.get(gpu.Name) is None:
            continue
        gpu.Cost = priceData[gpu.Name]
        gpus_.append(gpu)
    return gpus_
        
def CreateSeries(gpus: list):
    series = []
    for gpu in gpus:
        seriesData = {
            "GPU": gpu.Name,
            "1080p Ultra": gpu.fhdUltra,
            "1080p Medium": gpu.fhdMedium,
            "1440p Ultra": gpu.qhdUltra,
            "4K Ultra": gpu.fourkUltra,
            "Cost": gpu.Cost,
            "Cost Per Frame (1080p Ultra)": round(gpu.Cost / gpu.fhdUltra, 2),
            "Cost Per Frame (1080p Medium)": round(gpu.Cost / gpu.fhdMedium, 2),
            "Cost Per Frame (1440p Ultra)": round(gpu.Cost / gpu.qhdUltra, 2) if gpu.fhdUltra != 0.00 else 0,
            "Cost Per Frame (4K Ultra)": round(gpu.Cost / gpu.fourkUltra, 2) if gpu.fourkUltra != 0.00 else 0
        }
        if gpu.Name not in color_map:
            continue
        series.append(pd.DataFrame([seriesData]))
    return series

def LoadPrices(filename: str):
    prices = {}
    with open(filename, "r") as pricing_file:
        data = pricing_file.readlines()
    for line in data:
        val1, val2 = line.replace("\n", "").split(",")
        prices[val1] = float(val2)
    return prices

def Show_Figure(series: list, title: str, filename: str, currencySymbol: str = ""):
    dataFrame = pd.concat(series, ignore_index=True).sort_values("Cost Per Frame (1080p Ultra)", ascending=False)
    dataFrame.drop(dataFrame.index[dataFrame["Cost Per Frame (1080p Ultra)"] == 0], inplace=True)

    fhdBar = px.bar(dataFrame, y="GPU", x=["1080p Ultra", "Cost Per Frame (1080p Ultra)"], orientation='h', text_auto=True, color="GPU",
        color_discrete_map=color_map
    )
    fhdBar.update_traces(showlegend=False, texttemplate=["%{value} FPS", currencySymbol + "%{value}"], textposition=["outside", "outside"])
    fhdTraces = []
    for trace in range(len(fhdBar["data"])):
        fhdTraces.append(fhdBar["data"][trace])

    dataFrame = pd.concat(series, ignore_index=True).sort_values("Cost Per Frame (1440p Ultra)", ascending=False)
    dataFrame.drop(dataFrame.index[dataFrame["Cost Per Frame (1440p Ultra)"] == 0], inplace=True)
    
    qhdBar = px.bar(dataFrame, y="GPU", x=["1440p Ultra", "Cost Per Frame (1440p Ultra)"], orientation='h', text_auto=True, color="GPU",
        color_discrete_map=color_map
    )
    qhdBar.update_traces(showlegend=False, texttemplate=["%{value} FPS", currencySymbol + "%{value}"], textposition=["outside", "outside"])

    qhdTraces = []
    for trace in range(len(qhdBar["data"])):
        qhdTraces.append(qhdBar["data"][trace])


    dataFrame = pd.concat(series, ignore_index=True).sort_values("Cost Per Frame (4K Ultra)", ascending=False)
    dataFrame.drop(dataFrame.index[dataFrame["Cost Per Frame (4K Ultra)"] == 0], inplace=True)

    fourKBar = px.bar(dataFrame, y="GPU", x=["4K Ultra", "Cost Per Frame (4K Ultra)"], orientation='h', text_auto=True, color="GPU",
        color_discrete_map=color_map
    )
    fourKBar.update_traces(showlegend=False, texttemplate=["%{value} FPS", currencySymbol + "%{value}"], textposition=["outside", "outside"],name="Markers and Text" )

    fourKTraces = []
    for trace in range(len(fourKBar["data"])):
        fourKTraces.append(fourKBar["data"][trace])

    final_figure = make_subplots(
        rows=1, cols=3,
        subplot_titles=("1080p Ultra", "1440p Ultra", "4K Ultra"),
        x_title="Cost Per Frame | FPS<br>Performance data is from TomsHardware"
    )
    for trace in fhdTraces: final_figure.append_trace(trace, row=1, col=1)
    for trace in qhdTraces: final_figure.append_trace(trace, row=1, col=2)
    for trace in fourKTraces: final_figure.append_trace(trace, row=1, col=3)


    final_figure.update_layout(
        barmode="overlay", template="plotly_dark", title=title
    )
    final_figure.update_traces(texttemplate=["%{value} FPS", currencySymbol + "%{value}"])
    final_figure.write_image(filename, width=1920, height=1080, format="png")


if __name__ == "__main__":
    # Assumes GPU,Price. See examples in ./pricing_data

    # May be useful for getting this data:
    # https://github.com/pelpadesa/gpu-ebay-pricing
    now = datetime.datetime.now()
    currentDateStr = now.strftime(f"%B %d %Y")

    gpus = LoadGPUs("./pricing_data/US_Newegg.csv")
    series = CreateSeries(gpus)
    Show_Figure(series=series, title=f"USA Newegg Cost Per Frame (USD) | {currentDateStr}", currencySymbol="$", filename = "images/US_Newegg.png")
    







