export function getResourceName(type){
    switch (type) {
        case "1": return "Supplies"
        case "2": return "Components"
        case "3": return "Man Power"
        case "4": return "Rare Materials"
        case "5": return "Fuel"
        case "6": return "Electronics"
        case "20": return "Money"
        case "trp": return "Total Resource Production"
    }
}

export function getResourceColour(type){
    switch (type){
        case "1": return [51,77,0]
        case "2": return [37, 150, 190]
        case "4": return [255,169,94]
        case "5": return [255,84,67]
        case "6": return [6, 122, 0]
        case "20": return [255, 254, 0]
        case "trp": return [0, 0, 0]
    }
}