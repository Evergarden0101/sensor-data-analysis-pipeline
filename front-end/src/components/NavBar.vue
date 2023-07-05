<template>
    <div class="nav-bar">
        <router-link to="/" >
            <button>Home</button>
        </router-link>
        <router-link to="/eeg-meg">
            <button>EEG/MEG DATA</button>
        </router-link>
        <router-link to="/ecg">
            <button>ECG DATA</button>
        </router-link>
        <router-link to="/emg">
            <button>EMG DATA</button>  
        </router-link>
    </div>
</template>

<script>
export default{
    name: "NavBar",
}
</script>