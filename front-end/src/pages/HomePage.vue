<template>
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">

    <title>Hello, world!</title>
  </head>
  <body>
    <div class="container">
      <div class="row mb-5">
        <h1>Welcome to the sensor data pipeline for the labelling and monitoring of bruxism events!</h1>
      </div>
      <div class="row align-items-center justify-content-center mb-5 mt-5">
        <div class="col-12">
          <ul class="progressbar">
            <li class="">Data upload</li>
            <li class="">Sleep Stage Classification</li>
            <li class="">Brux Classification Dashboard</li>
            <li class="">Brux Events Monitoring</li>
          </ul>
        </div>
      </div>
      <div class="col-12 text-center">
        <button type="button" class="btn btn-primary">Start</button>
      </div>
    </div>
  </body>
</template>

<script>
export default {
    name: 'HomePage',
    components: {

    },
};
</script>

<style>
.progressbar{
  counter-reset: step;

}
.progressbar li {
  list-style-type: none;
  float: left;
  width: 25%;
  position: relative;
  text-align: center;
}
.progressbar li:before{
  content: counter(step);
  counter-increment: step;
  width: 40px;
  height: 40px;
  line-height: 40px;
  border: 2px solid #ddd;
  display: block;
  text-align: center;
  margin: 0 auto 10px auto;
  border-radius: 50%;
  background-color: white;

}
.progressbar li:after{
  content: '';
  position: absolute;
  width: 100%;
  height: 2px;
  background-color: #ddd;
  top: 20px;
  left:-50%;
  z-index:-1;
}
.progressbar li:first-child:after{
  content: none;
}
.progressbar li.active{
  color:darkblue;
}
.progressbar li.active:before{
  border-color: darkblue;
}
.progressbar li.active + li:after{
  background-color: darkblue;
}


</style>
  