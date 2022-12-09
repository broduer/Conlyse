export function get_combined(arrays, key) {
    let merged = {};
    let combined = {};
    for(let i=0; i<arrays[0].length; i++) {
        combined = arrays[0][i]
        for (let j=0; j<arrays.length; j++){
            let arr = arrays[j]
            combined = Object.assign(combined, arr.find((itmInner) => itmInner[key] === combined[key]))
        }
        merged[combined[key]] = combined
    }
    return merged
}

