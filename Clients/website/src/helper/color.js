import {theme} from "./theme";
export function getActionColor(number){
    if (number < 0) {
        return(theme.palette.error.main)
    }else if (number > 0){
        return (theme.palette.success.main)
    }else return (theme.palette.text.primary)
}
export function getResourceColor(number){
    switch (number){
        case 2: return(theme.palette.resources.supplies)
        case 3: return(theme.palette.resources.components)
        case 5: return(theme.palette.resources.rare_materials)
        case 6: return(theme.palette.resources.fuel)
        case 7: return(theme.palette.resources.electronics)
    }
}
export function getCountryColor(number){
    const c = [
        "#55a64d",
        "#985792",
        "#3445c9",
        "#a0004e",
        "#e492c6",
        "#3c33f4",
        "#61b26c",
        "#4912a4",
        "#fa85a0",
        "#f5f076",
        "#ec72fc",
        "#b1a9da",
        "#7eab1e",
        "#d1479d",
        "#746160",
        "#e1d177",
        "#3c05f7",
        "#c6382b",
        "#14f012",
        "#bd8d49",
        "#05b390",
        "#c50bab",
        "#182cbb",
        "#e2c100",
        "#c37b50",
        "#e437e5",
        "#17cc77",
        "#6480ad",
    ]
    const colors = c.concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c).concat(c)
    let color = colors[number]
    if (colors.length >= number) return color
}