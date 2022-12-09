
export function getDatefromTimestamp(timestamp, format) {
    let ts_ms = timestamp * 1000;

    // initialize new Date object
    let date_ob = new Date(ts_ms);

    // year as 4 digits (YYYY)
    let year = date_ob.getFullYear();

    // month as 2 digits (MM)
    let month = ("0" + (date_ob.getMonth() + 1)).slice(-2);

    // date as 2 digits (DD)
    let date = ("0" + date_ob.getDate()).slice(-2);

    // hours as 2 digits (hh)
    let hours = ("0" + date_ob.getHours()).slice(-2);

    // minutes as 2 digits (mm)
    let minutes = ("0" + date_ob.getMinutes()).slice(-2);

    // seconds as 2 digits (ss)
    let seconds = ("0" + date_ob.getSeconds()).slice(-2);


    switch (format) {
        case "D.M.Y": return (`${date}.${month}.${year}`)
        case "h:m: D.M.Y": return (`${hours}:${minutes} ${date}.${month}.${year}`)
        case "h:m:s": return (`${hours}:${minutes}:${seconds}`)
        case "h:m": return (`${hours}:${minutes}`)
        default: return (`${date}`)
    }

}

export function getDifference(timestamp_start, timestamp_end, format){
    let difference = timestamp_end - timestamp_start
    let days = difference / (3600*24)
    switch (format){
        case "D": return Math.floor(days)
        case "D_c": return Math.round(days * 100) / 100
        default: return difference
    }
}

export function getClosestTime(timestamp_array, timestamp){
    return timestamp_array.reduce((a, b) => {
        return Math.abs(b - timestamp) < Math.abs(a - timestamp) ? b : a;
    })
}

export function getRealtime(timestamp_start, timestamp_current, speed){
    let date_start = new Date(timestamp_start);
    let date_end = new Date(timestamp_current);

    let difference = date_end.getTime() - date_start.getTime()

    let realtime_difference = difference / speed

    return timestamp_start + realtime_difference
}