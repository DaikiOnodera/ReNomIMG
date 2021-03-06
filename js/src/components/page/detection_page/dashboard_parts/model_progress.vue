<template>
  <div id="model-progress"
      v-bind:class='{emphasizeItem: model.model_id==$store.state.selected_model_id}'>
    <div class="value-item">
      <div class="label">
        Model ID
      </div>
      <div class="value">
      <span class="dynamic-label">{{ model.model_id }}</span>
      </div>
    </div>

    <div class="value-item">
      <div class="label">
        Epoch
      </div>
      <div class="value"
        v-if="model.running_state!==running_state['starting']">
        <span class="dynamic-label">{{model.last_epoch}}</span>/{{model.hyper_parameters['total_epoch']}}
      </div>
      <div class="value"
        v-if="model.running_state===running_state['starting']">
        -/-
      </div>
    </div>

    <div class="value-item">
      <div class="label">
        Batch
      </div>
      <div class="value"
        v-if="model.running_state!==running_state['starting']">
        <span class="dynamic-label">{{model.last_batch}}</span>/{{model.total_batch}}
      </div>
      <div class="value"
        v-if="model.running_state===running_state['starting']">
        -/-
      </div>
    </div>

    <div class="progress-bar-area">
      <div class="progress-bar-back">
        <div class="progress">
          <div class="progress-bar progress-bar-striped" role="progressbar"
            v-bind:class="{'progress-bar-animated' : model.running_state===running_state['training']}">
          </div>
        </div>
      </div>
    </div>

    <div class="value-item">
      <div class="label">
        <span v-if="model.running_state===running_state['starting']">
          Starting...
        </span>
        <span v-else-if="model.running_state===running_state['training']">
          Train Loss
        </span>
        <span v-else-if="model.running_state===running_state['validating']">
          Validating
        </span>
        <span v-else-if="model.running_state===running_state['stopping']">
          Stopping...
        </span>
      </div>

      <div class="value">
        <span class="dynamic-label" v-if="model.running_state===running_state['training']">
          {{round(model.last_train_loss, 1000).toFixed(3)}}
        </span>
        <span v-if="model.running_state!==running_state['training']">
          <div class="loader-wrapper">
            <div class="loader"></div>
          </div>
        </span>
      </div>
    </div>

    <div class="stop-button-area">
      <div class="stop-button" @click="show_stop_dialog=true"
        v-if="model.running_state!==running_state['stopping']">
        <!-- <i class="fa fa-pause-circle-o" aria-hidden="true"></i> -->
        <img :src="url" aria-hidden="true">
      </div>
    </div>

    <modal-box v-if='show_stop_dialog'
      @ok='stopModel'
      @cancel='show_stop_dialog=false'>
      <div slot='contents'>
        Would you like to stop Model ID: {{this.model.model_id}}?
      </div>
      <span slot="okbutton">
        <button id="delete_labels_button" class="modal-default-button"
          @click="stopModel">
          Stop
        </button>
      </span>
    </modal-box>
  </div>
</template>

<script>
import * as utils from '@/utils'
import ModalBox from '@/components/common/modalbox'

export default {
  name: 'modelProgress',
  components: {
    'modal-box': ModalBox
  },
  data: function () {
    return {
      url: require('../../../../../static/img/stop.png'),
      progress_bar_color: '#0099CE',
      running_state: {
        'training': 0,
        'validating': 1,
        'starting': 3,
        'stopping': 4
      },
      show_stop_dialog: false
    }
  },
  props: {
    'index': {
      type: Number,
      require: true
    },
    'model': {
      type: Object,
      require: true
    }
  },
  created: function () {
    if (!this.model.has_executed_progress_api) {
      this.$store.dispatch('updateProgress', {'model_id': this.model.model_id})
      this.model.has_executed_progress_api = true
    }
  },
  mounted: function () {
    this.updateProgressBar()
  },
  updated: function () {
    // This is for reserved model progress.
    if (!this.model.has_executed_progress_api) {
      this.$store.dispatch('updateProgress', {'model_id': this.model.model_id})
      this.model.has_executed_progress_api = true
    }
    this.updateProgressBar()
  },
  methods: {
    updateProgressBar: function () {
      const progress_bar_elm = document.getElementsByClassName('progress-bar-back')
      if (progress_bar_elm.length === 0) return

      const progress_bar_width = progress_bar_elm[0].clientWidth
      let current_width = this.model.last_batch / this.model.total_batch * progress_bar_width
      let e = document.getElementsByClassName('progress-bar')
      if (e && e[this.index]) {
        e[this.index].style.width = current_width + 'px'
      }
    },
    stopModel: function () {
      this.$store.dispatch('stopModel', {
        'model_id': this.model.model_id
      })
      this.model.running_state = this.running_state['stopping']
      this.show_stop_dialog = false
    },
    round: function (v, round_off) {
      return utils.round(v, round_off)
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/../node_modules/bootstrap/scss/bootstrap.scss';
#model-progress {
  $content-margin: 8px;

  $label-color: #666666;

  $progress-bar-width: 24%;
  $progress-bar-height: 11pt;
  $progress-bar-bg-color: #e8e8e8;
  $progress-bar-color: #0099ce;

  $stop-button-color: #999999;
  $stop-button-color-hover: #666666;

  width: 100%;
  display: flex;
  display: -webkit-flex;

  margin-top: $content-margin;

  .value-item {
    display: flex;
    display: -webkit-flex;
    flex-direction: column;
    -webkit-flex-direction: column;

   // width: 64px; 

    .label, .label span {
      color: $label-color;
      font-size: $content-inner-box-font-size;
      line-height: $content-inner-box-font-size;
    }

    .value, .value span {
      color:$font-color-label;
      font-size: $content-inner-box-font-size;
      line-height:  $content-inner-box-font-size;
      span.dynamic-label{
        color:#000000;
      }
    }
  }

  div.value-item:not(:first-child){
   margin-left:20px; 
  }

  .stop-button-area {
    position: relative;
    .stop-button {
      position: absolute;
      bottom: 5px;
      width: 13px;
      height: 13px;
      margin-left: calc(#{$content-margin}*3);
      line-height: $content-inner-box-font-size;
      font-size: $content-inner-box-font-size;
      color: $stop-button-color;
      cursor: pointer;
      img{
         height: 13px;
         width:13px;
      }
    }
    .stop-button:hover {
      color: $stop-button-color-hover;
    }
  }

  .progress-bar-area {
    position: relative;
    width: $progress-bar-width;
    height: calc(#{$content-inner-box-font-size} + #{$content-inner-box-font-size});
    margin-right: $content-margin;

      .progress{
        margin-top: 15%;
        margin-left: 10%;
        height: 9px;
        background-color: #21212157;
        border-radius: 0;
      }

      .progress-bar .progress-bar-striped {
        bottom: 2px;
        width: 100%;
        background-color: $status-running;
        border-radius: 1px;
        border-width: 1px;
        border-color: #a5a5a5;
        border-style: solid;
      }

    }

  .loader-wrapper{
    content: "";
    display: inline-block;
  }

  .loader {
    border: 3px solid $status-running; /* Light grey */
    border-top: 3px solid #f3f3f3; /* Bar color */
    border-radius: 50%;
    width: 10px;
    height: 10px;
    animation: spin 2s linear infinite;
  }

  @keyframes spin {
    0% {
      -webkit-transform: rotate(0deg);
      -ms-transform: rotate(0deg);
      transform: rotate(0deg);
    }
    100% {
      -webkit-transform: rotate(360deg);
      -ms-transform: rotate(360deg);
      transform: rotate(360deg);
    }
  }
}

.emphasizeItem {
    animation: emphasize 0.4s;
    animation-iteration-count: 1;
    animation-delay: 0.05s;
}
@keyframes emphasize {
    0%{background-color: #ffffff;}
    30%{background-color: rgba(0, 0, 0, 0.1);}
    100%{background-color: #ffffff;}
}
</style>
