import { createStore } from 'vuex';
import VuexPersistence from 'vuex-persist';
import localForage from 'localforage';

const vuexLocal = new VuexPersistence({
  storage: localForage,
  asyncStorage: true
});

// 创建一个新的 store 实例
const store = createStore({
  state () {
    return {
      patientId: 1,
      week: 1,
      day: 3,
      nightId: "",
      startStage: 0,
      endStage: 0,
      startPoint: 0,
      endPoint: Infinity,
      linePlotKey: 0,
      plotStart: 0,
      plotEnd: 0,
    }
  },
  mutations: {
    selectStage(state,payload) {
      state.startStage = payload.startStage;
      state.endStage = payload.endStage;
    },
    updataPoint(state,payload) {
      state.startPoint = payload.startPoint;
      state.endPoint = payload.endPoint;
    },
    updatePatientSeletion(state, payload){
      state.patientId = payload.patient_id;
      state.week = payload.week;
      state.nightId = payload.night_id;
    },
    updateLinePlotKey(state){
      state.linePlotKey++;
    },
    setLabelRange(state, payload){
      state.plotStart = payload.plotStart;
      state.plotEnd = payload.plotEnd;
    }
  },
  plugins: [vuexLocal.plugin],

})

export default store;