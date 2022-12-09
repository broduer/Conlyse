export default function getTrades(trades, countrys, game){
    for (let trade in trades){
        trade = trades[trade]
        trade["id"] = trade["tdid"]
        trade["pc"] = trade["am"] * trade["lm"]
        trade["ct"] = new Date((game["st"] + ((trade["ct"] - game["st"]) / game["sp"])) * 1000)
        trade["cn"] = countrys[trade["oid"]]["cn"]
        if (trade["b"]) trade["b"] = "Buy"
        else trade["b"] = "Sell"
    }
    return trades
}