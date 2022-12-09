export function getResourceName(type){
    switch (type) {
        case "2": return "Supplies"
        case "3": return "Components"
        case "5": return "Rare Materials"
        case "6": return "Fuel"
        case "7": return "Electronics"
        case "21": return "Money"
        case "trp": return "Total Resource Production"
    }
}

export function getResourceColour(type){
    switch (type){
        case "2": return [51,77,0]
        case "3": return [37, 150, 190]
        case "5": return [255,169,94]
        case "6": return [255,84,67]
        case "7": return [6, 122, 0]
        case "21": return [255, 254, 0]
        case "trp": return [0, 0, 0]
    }
}