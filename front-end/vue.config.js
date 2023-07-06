const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {        
    devServer: {
      headers: {
        'Access-Control-Allow-Origin': '*'            
      }
    }
  },
  chainWebpack: config => {
    // csv-loader
    config.module
      .rule('csv-loader')
      .test(/\.csv$/)
      .use('csv-loader')
        .loader('csv-loader')
        .end()
  },
})