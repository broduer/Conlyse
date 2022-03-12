export default function getHighValueCities(provinces){
    console.log(provinces)
    var provinces_sorted = Object.values(provinces)
    provinces_sorted.sort((a, b) => {
        return b["total"] - a["total"];
    });
    return provinces_sorted.splice(0, 10)
}
