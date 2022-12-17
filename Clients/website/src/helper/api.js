import axios from "axios";

const api = axios.create({
    baseURL: "http://localhost:4444/api/v2"
});

// Static API Endpoints
export const get_static_upgrades = () => api.get("/static/upgrade").then(res => res.data);
export const get_static_research = () => api.get("/static/research").then(res => res.data);
export const get_static_warfare_types = () => api.get("/static/warfare_types").then(res => res.data);
export const get_static_provinces = (map_id) => api.get(`/static/province/${map_id}`).then(res => res.data);
// Dynamic API Endpoints
export const get_games = () => api.get("/game/-1").then(res => res.data);

export const get_game = (game_id) => api.get(`/game/${game_id}`).then(res => res.data);

export const get_countrys = (game_id, mode, country_id, from_timestamp, until_timstamp) => api.get(`/countrys/${game_id}/${mode}/${country_id}/${from_timestamp}/${until_timstamp}`).then(res => res.data);
export const get_teams = (game_id) => api.get(`/team/${game_id}`).then(res => res.data);

export const get_provinces = (game_id, mode, unix_timestamp) => api.get(`/provinces/${game_id}/${mode}/${unix_timestamp}`).then(res => res.data);

export const get_trades = (game_id) => api.get(`/trade/${game_id}`).then(res => res.data);

