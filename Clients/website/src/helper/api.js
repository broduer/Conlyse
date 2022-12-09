import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:4444/api/v2"
});

// Static API Endpoints
export const getStaticUpgrades = () => api.get("/static/upgrade").then(res => res.data);
export const getStaticResearches = () => api.get("/static/research").then(res => res.data);
export const getStaticProvinces = (map_id) => api.get(`/static/province/${map_id}`).then(res => res.data);
// Dynamic API Endpoints
export const getGames = () => api.get("/game/-1").then(res => res.data);

export const getGame = (game_id) => api.get(`/game/${game_id}`).then(res => res.data);

export const getCountrys = (game_id, mode, country_id, from_timestamp, until_timstamp) => api.get(`/countrys/${game_id}/${mode}/${country_id}/${from_timestamp}/${until_timstamp}`).then(res => res.data);
export const getTeams = (game_id) => api.get(`/team/${game_id}`).then(res => res.data);

export const getProvinces = (game_id, mode, unix_timestamp) => api.get(`/provinces/${game_id}/${mode}/${unix_timestamp}`).then(res => res.data);

export const getTrades = (game_id) => api.get(`/trade/${game_id}`).then(res => res.data);

