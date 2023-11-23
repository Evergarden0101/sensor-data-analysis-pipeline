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
            target: 'http://127.0.0.1:5000/',
            // ws: true,
            changeOrigin: true
        },
        '^/api': {
          target: 'http://10.28.51.5:8080/',
          changeOrigin: true
        },
      },
    },
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
