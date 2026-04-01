import pandas as pd
import plotly.express as px

def run_plotly_dashboard(csv_path="output/data.csv"):
    df = pd.read_csv(csv_path)


    fig1 = px.bar(
        df.groupby("platform", as_index=False)["item_price"].mean(),
        x="platform",
        y="item_price",
        title="Precio promedio por plataforma"
    )
    fig1.show()


    fig2 = px.bar(
        df.groupby("platform", as_index=False)["delivery_fee"].mean(),
        x="platform",
        y="delivery_fee",
        title="Delivery fee promedio por plataforma"
    )
    fig2.show()


    eta = df.groupby("platform", as_index=False)[["eta_min", "eta_max"]].mean()
    fig3 = px.bar(
        eta,
        x="platform",
        y=["eta_min", "eta_max"],
        barmode="group",
        title="Tiempo estimado de entrega por plataforma"
    )
    fig3.show()