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

function getRandomHexColor(){
    let makeColorCode = '0123456789ABCDEF';
    let code = '';
    for (let count = 0; count < 6; count++) {
        code =code+ makeColorCode[Math.floor(Math.random() * 16)];
    }
    return code;
}

function decToHex(value) {
    if (value >= 255) {
        return 'FF';
    } else if (value <= 0) {
        return '00';
    } else {
        return value.toString(16).padStart(2, '0').toUpperCase();
    }
}

export function rgbToHex(r, g, b){
    return "0x" + decToHex(r) + decToHex(g) + decToHex(b);
}

export function rgbaToCustom({r, g, b, a}){
    if(!a) a = 0
    return [rgbToHex(r, g, b), a]
}

export function hexToRgb(hex) {
    let result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

export function customToRgba([hex, a]){
    return {...hexToRgb("#" + hex.slice(2)), "a": a}
}


export function customToCSS([hex, a]){
    let rgba = customToRgba([hex, a])
    return `rgba(${rgba.r}, ${rgba.g}, ${rgba.b}, ${a})`
}



export const color_schema = {
    "0": 0xA88618,
    "1": 0x871657,
    "2": 0x8DAABD,
    "3": 0x54C14C,
    "4": 0x7B8DA8,
    "5": 0x623821,
    "6": 0x5F8C83,
    "7": 0x212E34,
    "8": 0xDB9EB0,
    "9": 0xF2680,
    "10": 0x006E16,
    "11": 0x03DD1C,
    "12": 0xBB5DF9,
    "13": 0x4DE559,
    "14": 0x77F303,
    "15": 0xDF3C53,
    "16": 0x4424D6,
    "17": 0xFE5C79,
    "18": 0xB4310A,
    "19": 0x580022,
    "20": 0x7FFFDC,
    "21": 0x11066A,
    "22": 0x7432E5,
    "23": 0x500D92,
    "24": 0x75F513,
    "25": 0x7D2573,
    "26": 0xEE5393,
    "27": 0x7FDDBE,
    "28": 0x1A10B8,
    "29": 0x5BE18C,
    "30": 0x03E701,
    "31": 0xCD0E71,
    "32": 0xD4F0D2,
    "33": 0x630BE0,
    "34": 0x68A183,
    "35": 0x80CD0B,
    "36": 0xFB08A9,
    "37": 0xA23FE2,
    "38": 0x0D1B6F,
    "39": 0x91D812,
    "40": 0x47DF8A,
    "41": 0x99292B,
    "42": 0xB9BDE3,
    "43": 0xA8F2CC,
    "44": 0x5EA6C4,
    "45": 0xC4490F,
    "46": 0x006D91,
    "47": 0x669BCD,
    "48": 0xB650B2,
    "49": 0xBD1721,
    "50": 0x0915AB,
    "51": 0x7100DB,
    "52": 0xC1B62A,
    "53": 0x2C9342,
    "54": 0x311A2C,
    "55": 0xB7106E,
    "56": 0xB77F08,
    "57": 0x6A3EE5,
    "58": 0xA212A3,
    "59": 0x667363,
    "60": 0x783813,
    "61": 0x49B7C9,
    "62": 0x59A0EB,
    "63": 0xC9E839,
    "64": 0x4742CB,
    "65": 0x08CCF7,
    "66": 0x94A391,
    "67": 0x913574,
    "68": 0x203930,
    "69": 0xC51235,
    "70": 0x4BCB56,
    "71": 0x7D83C7,
    "72": 0xE74E1B,
    "73": 0x7360D8,
    "74": 0xBCC352,
    "75": 0xC42848,
    "76": 0xC1FA15,
    "77": 0xB25D82,
    "78": 0x40A3E4,
    "79": 0xF93E0F,
    "80": 0x4CA07B,
    "81": 0x4F7065,
    "82": 0x1B6FEA,
    "83": 0x8AECC9,
    "84": 0x2BBE9F,
    "85": 0x3CF864,
    "86": 0xE48CED,
    "87": 0xFCBD84,
    "88": 0x515EE2,
    "89": 0x4D1E05,
    "90": 0x277AC4,
    "91": 0xFB7B56,
    "92": 0x8AC4E9,
    "93": 0x1C53D3,
    "94": 0x1A7F0D,
    "95": 0xD89E8A,
    "96": 0xD77B12,
    "97": 0x8F071E,
    "98": 0x258F54,
    "99": 0x6858D,
    "100": 0x290681,
    "101": 0x34D4C0,
    "102": 0x22F3A6,
    "103": 0x1A5741,
    "104": 0x0FAEB0,
    "105": 0xFC6ED1,
    "106": 0xD7B45B,
    "107": 0x818719,
    "108": 0xAB9CDF,
    "109": 0x7F1132,
    "110": 0xC043A6,
    "111": 0xB98606,
    "112": 0xDB72C1,
    "113": 0x9F84C7,
    "114": 0x485EEA,
    "115": 0x5F5995,
    "116": 0x555F6D,
    "117": 0x785F7A,
    "118": 0x0B1A60,
    "119": 0x543074,
    "120": 0xAE4092,
    "121": 0xF5F60A,
    "122": 0xE1E14A,
    "123": 0xB05EF6,
    "124": 0x782352,
    "125": 0x7752E5,
    "126": 0x3765B4,
    "127": 0x48588D,
    "128": 0x4D1519,
    "129": 0x4BBEB2,
    "130": 0xF89AD2,
    "131": 0xDD010A,
    "132": 0x923774,
    "133": 0xD1BA90,
    "134": 0xB070F2,
    "135": 0xB43347,
    "136": 0x5BD329,
    "137": 0x6C82AD,
    "138": 0x96F657,
    "139": 0x97BEB8,
    "140": 0x7D5407,
    "141": 0x6939C7,
    "142": 0x784A8B,
    "143": 0x61F76D,
    "144": 0x0C334A,
    "145": 0x82EC02,
    "146": 0xCB6F7C,
    "147": 0x10649C,
    "148": 0x00CF2B,
    "149": 0xC60A45,
    "150": 0x07E012
}
