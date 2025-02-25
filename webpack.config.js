const package = require('./package.json');
const path = require('path');
// const version = require('./package.json').version;
const SveltePreprocess = require('svelte-preprocess');

// Custom webpack rules
const rules = [
  { test: /\.tsx?$/, loader: 'ts-loader' },
  { test: /\.js$/, loader: 'source-map-loader' },
  { test: /\.css$/, use: ['style-loader', 'css-loader'] },
  {
    test: /\.svelte$/,
    loader: 'svelte-loader',
    options: {
      preprocess: SveltePreprocess({
        postcss: {
          plugins: [require('tailwindcss'), require('autoprefixer')]
        }
      })
    }
  },
  {
    // required to prevent errors from Svelte on Webpack 5+, omit on Webpack 4
    test: /node_modules\/svelte\/.*\.mjs$/,
    resolve: {
      fullySpecified: false
    }
  },
  {
    test: /\.svg$/,
    loader: 'svg-url-loader'
  }
];

// Packages that shouldn't be bundled but loaded at runtime
const externals = Object.keys(package.jupyterlab.sharedPackages);

const resolve = {
  alias: {
    svelte: path.resolve('node_modules', 'svelte')
  },
  extensions: [
    '.webpack.js',
    '.web.js',
    '.ts',
    '.js',
    '.svelte',
    '.css',
    '.svg'
  ],
  mainFields: ['svelte', 'browser', 'module', 'main'],
  conditionNames: ['svelte']
};

module.exports = [
  /**
   * Lab extension
   *
   * This builds the lib/ folder with the JupyterLab extension.
   */
  {
    entry: './src/index.ts',
    output: {
      filename: 'index.js',
      path: path.resolve(__dirname, 'lib'),
      libraryTarget: 'amd',
      publicPath: ''
    },
    module: {
      rules: rules
    },
    externals,
    resolve
  }
];
