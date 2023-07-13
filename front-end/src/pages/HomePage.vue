<template>
    <body>
        <div class="container">
        <div class="steps">
            <span class="circle">Data upload</span>
            <span class="circle">Sleep Stage Classification</span>
            <span class="circle">Brux Classification Dashboard</span>
            <span class="circle">Brux Events Monitoring</span>
        </div>
        <div class="buttons">
            <router-link :to="'/upload/'" style="margin-right: 20px;">
                <button class="button">Start</button>
            </router-link>
        </div>
        </div>
    </body>
  </template>
  
  <style>
  /* Import Google font - Poppins */
  @import url("https://fonts.googleapis.com/css2?family=Poppins:wght@200;300;400;500;600;700&display=swap");
  * {
    margin: 0;
    padding: 0px;
    box-sizing: border-box;
    font-family: "Poppins", sans-serif;
  }
  body {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f6f7fb;
  }
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 40px;
    max-width: 400px;
    width: 100%;
  }
  .container .steps {
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: space-between;
    position: relative;
  }
  .steps .circle {
    margin-right: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 80px;
    width: 80px;
    color: #4070f4;
    font-size: 22px;
    font-weight: 500;
    border-radius: 50%;
    background: #fff;
    border: 4px solid #4070f4;
    transition: all 200ms ease;
    transition-delay: 0s;
    font-size: 10px;
    text-align: center;
  }
  
  .container .buttons {
    display: flex;
    gap: 20px;
  }
  .buttons button {
    padding: 8px 25px;
    background: #4070f4;
    border: none;
    border-radius: 8px;
    color: #fff;
    font-size: 16px;
    font-weight: 400;
    cursor: pointer;
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.05);
    transition: all 200ms linear;
  }

  </style>

<script>
export default {
    name: 'HomePage',
    components: {

    },
};
</script>
  