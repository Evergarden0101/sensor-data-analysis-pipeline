import { createStore } from 'vuex';
import VuexPersistence from 'vuex-persist';
import localForage from 'localforage';
import {clone} from 'pouchdb-utils';

const vuexLocal = new VuexPersistence({
  storage: localForage,
  asyncStorage: true,
  reducer: (state) => clone(state),
});

// 创建一个新的 store 实例
const store = createStore({
  state () {
    return {
      patientId: 1,
      week: 0,
      day: 3,
      nightId: "",
      recorder: "",
      startStage: 0,
      endStage: 0,
      startPoint: 0,
      endPoint: Infinity,
      linePlotKey: 0,
      plotStart: 0,
      plotEnd: 0,
      checkedMR: true,
      checkedML: true,
      labels: null,
      samplingRate: 1000,
      bruxLabelKey: 0,
      studyPrecision: '--',
      patientPrecision: '--',
      nightImg: '',
      weekImg: '',
      selectedEvent: null,
      lineplotData: null,
      eventNo: 1,
      predFinish: false,
      isMonitoringAllowed: 0,
      settingsExist: 0,
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
      state.recorder = payload.recorder;
    },
    updateLinePlotKey(state){
      state.linePlotKey++;
    },
    setLabelRange(state, payload){
      state.plotStart = payload.plotStart;
      state.plotEnd = payload.plotEnd;
    },
    selectMR(state, payload){
      state.checkedMR = payload;
    },
    selectML(state, payload){
      state.checkedML = payload;
    },
    saveLabels(state, payload){
      state.labels = payload;
    },
    updateSamplingRate(state, payload){
      state.samplingRate = payload;
    },
    updateBruxLabelKey(state){
      state.bruxLabelKey++;
    },
    clearLabels(state){
      state.labels = null;
    },
    updateStudyPrecision(state, payload){
      state.studyPrecision= payload;
    },
    updatePatientPrecision(state, payload){
      state.patientPrecision = payload;
    },
    getNightImg(state, payload){
      state.nightImg = payload;
    },
    selectEvent(state,payload){
      state.selectedEvent = payload;
    },
    saveLineplotData(state,payload){
      state.lineplotData = payload;
    },
    getWeekImg(state, payload){
      state.weekImg = payload;
    },
    setEventNo(state, payload){
      state.eventNo = payload;
    },
    setPredFinish(state, payload){
      state.predFinish = payload;
    },
    updateIsMonitoringAllowed(state, payload){
      state.isMonitoringAllowed = payload;
    },
    updateSettingsExist(state, payload){
      state.settingsExist = payload;
    }
  },
  plugins: [vuexLocal.plugin],

})

export default store;