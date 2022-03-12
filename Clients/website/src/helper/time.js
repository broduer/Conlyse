
export function getDatefromTimestamp(timestamp, format) {
    var ts_ms = timestamp * 1000;

    // initialize new Date object
    var date_ob = new Date(ts_ms);

    // year as 4 digits (YYYY)
    var year = date_ob.getFullYear();

    // month as 2 digits (MM)
    var month = ("0" + (date_ob.getMonth() + 1)).slice(-2);

    // date as 2 digits (DD)
    var date = ("0" + date_ob.getDate()).slice(-2);

    // hours as 2 digits (hh)
    var hours = ("0" + date_ob.getHours()).slice(-2);

    // minutes as 2 digits (mm)
    var minutes = ("0" + date_ob.getMinutes()).slice(-2);

    // seconds as 2 digits (ss)
    var seconds = ("0" + date_ob.getSeconds()).slice(-2);


    switch (format) {
        case "D.M.Y": return (`${date}.${month}.${year}`)
        case "h:m: D.M.Y": return (`${hours}:${minutes} ${date}.${month}.${year}`)
        case "h:m:s": return (`${hours}:${minutes}:${seconds}`)
        case "h:m": return (`${hours}:${minutes}`)
        default: return (`${date}`)
    }

}

export function getDifference(timestamp_start, timestamp_end, format){
    var date_start = new Date(timestamp_start);
    var date_end = new Date(timestamp_end);

    var difference = date_end.getTime() - date_start.getTime()

    var days = Math.floor(difference / (3600*24))

    switch (format){
        case "D": return days + 1
        default: return difference
    }
}

export function getRealtime(timestamp_start, timestamp_current, speed){
    var date_start = new Date(timestamp_start);
    var date_end = new Date(timestamp_current);

    var difference = date_end.getTime() - date_start.getTime()

    let realtime_difference = difference / speed

    return timestamp_start + realtime_difference
}