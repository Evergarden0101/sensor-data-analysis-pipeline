<template>
    <div class="nav-bar">
        <router-link to="/" style="margin-right: 20px;">
            <button>Home</button>
        </router-link>
        <router-link to='/filtering/' style="margin-right: 20px;">
            <button>Filtering</button>  
        </router-link>

        <router-link to='/events-classification/' style="margin-right: 20px;">
            <button>Events Classification</button>  
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