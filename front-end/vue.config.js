const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {        
    devServer: {
      headers: {
        'Access-Control-Allow-Origin': '*'            
      },
      proxy: {
        '': {
            target: 'http://127.0.0.1:5000',
            // ws: true,
            changeOrigin: true
        }
      },
    },
  },
})