export function getCombinedProvinces(static_provinces, provinces) {
    let arr1 = Object.values(static_provinces)
    let arr2 = Object.values(provinces)
    let merged = [];

    for(let i=0; i<arr1.length; i++) {
        merged.push({
            ...arr1[i],
            ...(arr2.find((itmInner) => itmInner.province_location_id === arr1[i].province_location_id))}
        );
    }
    return merged
}