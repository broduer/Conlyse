import {useFetch} from "../../helper/useFetch";
import {getDifference} from "../../helper/time";

export function useGame(game_id) {
    let datas = {
        "scenario": useFetch(`http://127.0.0.1:4444/api/v1/static/scenario`),
        "game": useFetch(`http://127.0.0.1:4444/api/v1/game?game_id=${game_id}`),
    }
    let loading = false;
    for (let data in datas) {
        data = datas[data]
        if (data.isLoading || data.data === null){
            loading = true
        }
    }
    return ({datas, loading})
}

export function useDashboard(game, scenario) {
    const game_id = game["game_id"]
    let datas = {
        "trades": useFetch(`http://127.0.0.1:4444/api/v1/trade?game_id=${game_id}`),
        "scenarios": scenario,
        "static_provinces": useFetch(`http://127.0.0.1:4444/api/v1/static/province?map_id=${scenario["map_id"]}`),
        "countrys": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}`),
        "teams": useFetch(`http://127.0.0.1:4444/api/v1/team?game_id=${game_id}`),
        "provinces": useFetch(`http://127.0.0.1:4444/api/v1/province?game_id=${game_id}&day=${getDifference(game["start_time"], game["current_time"], "D")}`),
        "provinces_buildings": useFetch(`http://127.0.0.1:4444/api/v1/province?game_id=${game_id}&day=${getDifference(game["start_time"], game["current_time"], "D")}&value&ranked`),
        "game": game,
        "upgrades": useFetch(`http://127.0.0.1:4444/api/v1/static/upgrade`),
        "countrys_adv": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}&economy=true`),
    }
    let loading = false;
    for (let data in datas) {
        if ("game" === data) continue
        data = datas[data]
        if (data.isLoading || data.data === null){
            loading = true
        }
    }
    return ({datas, loading})
}

export function useCountrys(game) {
    const game_id = game["game_id"]
    let datas = {
        "countrys": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}`),
        "teams": useFetch(`http://127.0.0.1:4444/api/v1/team?game_id=${game_id}`),
        "countrys_adv": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}&economy=true&single&day=${getDifference(game["start_time"], game["current_time"], "D")}`),
    }
    let loading = false;
    for (let data in datas) {
        if ("game" === data) continue
        data = datas[data]
        if (data.isLoading || data.data === null){
            loading = true
        }
    }
    return ({datas, loading})
}

export function useCountry(game, scenario, country_id) {
    const game_id = game["game_id"]
    let datas = {
        "countrys": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}`),
        "teams": useFetch(`http://127.0.0.1:4444/api/v1/team?game_id=${game_id}`),
        "countrys_adv": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}&economy=true&lastdays=${getDifference(game["start_time"], game["current_time"], "D")}&day=${getDifference(game["start_time"], game["current_time"], "D")}`),
        "countrys_rs": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}&country_id=${country_id}&research`),
        "static_provinces": useFetch(`http://127.0.0.1:4444/api/v1/static/province?map_id=${scenario["map_id"]}`),
        "provinces": useFetch(`http://127.0.0.1:4444/api/v1/province?game_id=${game_id}&owner_id=${country_id}&day=${getDifference(game["start_time"], game["current_time"], "D")}`),
        "countrys_stats": useFetch(`http://127.0.0.1:4444/api/v1/country?game_id=${game_id}&country_id=${country_id}&stats&day=${getDifference(game["start_time"], game["current_time"], "D")}`),

    }
    let loading = false;
    for (let data in datas) {
        if ("game" === data) continue
        data = datas[data]
        if (data.isLoading || data.data === null){
            loading = true
        }
    }
    return ({datas, loading})
}