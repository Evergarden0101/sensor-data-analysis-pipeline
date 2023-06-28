<template>
    <h1>This is the Home Page</h1>
    <div class="hp-icons-container">
        <router-link :to="'/eeg-meg/'">
            <button>EEG/MEG DATA</button>  
        </router-link>
        
        <router-link :to="'/ecg/'">
            <button>ECG DATA</button> 
        </router-link>
    </div>
  </template>
  
  <script>
  
export default {
    name: 'HomePage',
};
  </script>
  