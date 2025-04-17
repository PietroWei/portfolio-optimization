import plotly.express as px
import plotly.graph_objects as go

def plot_efficient_frontier(data, model, include_rf):
    # Enhanced Efficient Frontier plotting with legend
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['risk'], 
        y=data['return'], 
        mode="markers", 
        name="Portfolios",
        marker=dict(size=8, color=data['sharpe_ratio'], colorscale="Viridis", showscale=True)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], 
        y=[0, 1], 
        mode="lines", 
        name="Efficient Frontier"
    ))
    fig.update_layout(
        title=f"Efficient Frontier ({model})",
        xaxis_title="Risk (Standard Deviation)",
        yaxis_title="Return",
        legend_title="Legend"
    )
    fig.show()

def plot_allocation(weights):
    # Enhanced pie chart with legend
    fig = px.pie(
        values=weights, 
        names=weights.index, 
        title="Portfolio Allocation",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(
        legend_title="Assets",
        showlegend=True
    )
    fig.show()

def plot_rolling_metrics(data, window=30):
    # Enhanced rolling metrics visualization with legends
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['rolling_volatility'], 
        mode="lines", 
        name="Rolling Volatility"
    ))
    fig.add_trace(go.Scatter(
        x=data.index, 
        y=data['rolling_sharpe'], 
        mode="lines", 
        name="Rolling Sharpe Ratio"
    ))
    fig.update_layout(
        title=f"Rolling Metrics (Window: {window} days)",
        xaxis_title="Date",
        yaxis_title="Metric Value",
        legend_title="Metrics"
    )
    fig.show()