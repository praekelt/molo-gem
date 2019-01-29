'use strict';

var gulp              =   require('gulp'),
    glob              =   require('glob'),
    sass              =   require('gulp-sass'),
    sassLint          =   require('gulp-sass-lint'),
    sassGlob          =   require('gulp-sass-glob'),
    cleanCSSMinify    =   require('gulp-clean-css'),
    autoprefixer      =   require('gulp-autoprefixer'),
    bless             =   require('gulp-bless'),
    watch             =   require('gulp-watch'),
    rename            =   require('gulp-rename'),
    gzip              =   require('gulp-gzip'),
    notify            =   require('gulp-notify'),
    sourcemaps        =   require('gulp-sourcemaps'),
    livereload        =   require('gulp-livereload'),
    minify            =   require('gulp-minify'),
    pixrem            =   require('gulp-pixrem'),
    svgmin            =   require('gulp-svgmin'),
    del               =   require('del'),
    gutil             =   require('gulp-util'),
    uglify            =   require('gulp-uglify'),
    sassPaths = [
        'gem/styles/gem/base_style.scss',
        'gem/styles/gem/base_style-rtl.scss',
        'gem/styles/gem-malawi/malawi.scss',

        'gem/styles/gem-rwanda/nn.scss',
        'gem/styles/gem-rwanda/enhanced-nn.scss',

        'gem/styles/maintenance.scss',

        'gem/styles/gem-springster/01_springster.s+(a|c)ss',
        'gem/styles/gem-springster/02_springster-rtl.s+(a|c)ss',
        'gem/styles/gem-springster/03_state.s+(a|c)ss',
        'gem/styles/gem-springster/04_state-320.s+(a|c)ss',
        'gem/styles/gem-springster/05_no-script-state.s+(a|c)ss',
        'gem/styles/gem-springster/@font-face-baton.s+(a|c)ss',
    ],
    authSassPaths = [
        'gem/styles/gem-springster/auth/springster.feature.scss',
        'gem/styles/gem-springster/auth/springster.enhanced.scss',
        'gem/styles/gem-malawi/auth/zathu.feature.scss',
        'gem/styles/gem-malawi/auth/zathu.enhanced.scss',
        'gem/styles/gem-rwanda/auth/rwanda.feature.scss',
        'gem/styles/gem-rwanda/auth/rwanda.enhanced.scss'
    ],
    sassDest = {
         prd: 'gem/static/css/prd',
         dev: 'gem/static/css/dev',
    },
    authSassDest = {
         auth: 'gem/styles/auth-compiled'
    };

    function styles(env) {
      var s = gulp.src(env === 'auth' ? authSassPaths : sassPaths);
      var isDev = env === 'dev';
      if (isDev)
        s = s
            .pipe(sourcemaps.init());
        s = s
        .pipe(sassGlob())
        .pipe(sass().on('error', sass.logError))
        .pipe(bless())
        .pipe(cleanCSSMinify())
        .pipe(pixrem());
        if (isDev)
        s = s
        .pipe(sourcemaps.write('/maps'));
        return s
        .pipe(gutil.env.type !== 'ci' ? notify({ message: `Styles task complete: ${env}` }) : gutil.noop())
        .pipe(gulp.dest(env === 'auth' ? authSassDest[env] : sassDest[env]));
    }
    gulp.task('styles:prd', function() {
      return styles('prd');
    });
    gulp.task('styles:dev', function() {
      return styles('dev');
    });
    gulp.task('styles:auth', function() {
      return styles('auth');
    });

    // Minify JS
    gulp.task('compress', function() {
      return gulp.src([
          'gem/static/js/springster.js',
          'gem/static/js/nn.js',
          'gem/static/js/modeladmin/index.js'
        ])
        .pipe(rename({
          suffix: "-min",
          extname: ".js"
        }))
        .pipe(uglify())
        .on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
        .pipe(gulp.dest('gem/static/js/dest'))
    });

  gulp.task('watch', function() {
      livereload.listen();
      gulp.watch(['gem/styles/**/*.scss',' gem/static/js/springster.js'], ['styles']);
  });
  gulp.task('styles', ['styles:dev', 'styles:prd', 'styles:auth']);
  gulp.task('default', ['styles', 'compress']);
