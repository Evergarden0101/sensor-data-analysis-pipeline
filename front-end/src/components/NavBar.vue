<template>
    <div class="nav-bar">
        <router-link to="/" style="margin-right: 20px;">
            <button>Home</button>
        </router-link>
        <router-link to='/sleep/' style="margin-right: 20px;">
            <button>Sleep Stage Classification</button>  
        </router-link>

        <router-link to='/bruxism/' style="margin-right: 20px;">
            <button>Bruxism Detection</button>  
        </router-link>
        
        <router-link to='/treatment/' style="margin-right: 20px;">
            <button>Treatment Analysis</button> 
        </router-link>
    </div>
</template>

<script>
export default{
    name: "NavBar",
}
</script>