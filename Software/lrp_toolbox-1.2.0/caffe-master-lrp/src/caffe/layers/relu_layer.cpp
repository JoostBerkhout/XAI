#include <algorithm>
#include <vector>

#include "caffe/layer.hpp"
#include "caffe/vision_layers.hpp"

namespace caffe {

template <typename Dtype>
void ReLULayer<Dtype>::Forward_cpu(const vector<Blob<Dtype>*>& bottom,
    const vector<Blob<Dtype>*>& top) {
  const Dtype* bottom_data = bottom[0]->cpu_data();
  Dtype* top_data = top[0]->mutable_cpu_data();
  const int count = bottom[0]->count();
  Dtype negative_slope = this->layer_param_.relu_param().negative_slope();
  for (int i = 0; i < count; ++i) {
    top_data[i] = std::max(bottom_data[i], Dtype(0))
        + negative_slope * std::min(bottom_data[i], Dtype(0));
  }
}

template <typename Dtype>
void ReLULayer<Dtype>::Backward_cpu(const vector<Blob<Dtype>*>& top,
    const vector<bool>& propagate_down,
    const vector<Blob<Dtype>*>& bottom) {
  if (propagate_down[0]) {
    const Dtype* bottom_data = bottom[0]->cpu_data();
    const Dtype* top_diff = top[0]->cpu_diff();
    Dtype* bottom_diff = bottom[0]->mutable_cpu_diff();
    const int count = bottom[0]->count();
    Dtype negative_slope = this->layer_param_.relu_param().negative_slope();
    for (int i = 0; i < count; ++i) {
      bottom_diff[i] = top_diff[i] * ((bottom_data[i] > 0)
          + negative_slope * (bottom_data[i] <= 0));
    }
  }
}


template <typename Dtype>
void ReLULayer<Dtype>::Backward_Relevance_cpu(const vector<Blob<Dtype>*>& top,
      const vector<bool>& propagate_down, const vector<Blob<Dtype>*>& bottom, 
	  const int layerindex, const relpropopts & ro , const std::vector<int> & classinds, const bool thenightstartshere)
{
	
	switch(ro.relpropformulatype)
	{
		case 0:
		case 2:
		case 6:
		case 8:
		case 10:
		case 11: // 11 is gradient in the demonstrator
		case 12:
		case 14:
		case 18:
		case 20:
		case 54: 
		case 56: 
		case 58: 
		case 60: 
		case 22:
		{
			  //if (propagate_down[0]) {
			    const Dtype* bottom_data = bottom[0]->cpu_data();
			    const Dtype* top_diff = top[0]->cpu_diff();
			    Dtype* bottom_diff = bottom[0]->mutable_cpu_diff();
			    const int count = bottom[0]->count();
			    //Dtype negative_slope = this->layer_param_.relu_param().negative_slope();
			    for (int i = 0; i < count; ++i) {
			      bottom_diff[i] = top_diff[i];
			    }
			 // }

		}
		break;
		case 26: //zeiler
		{
			    const Dtype* bottom_data = bottom[0]->cpu_data();
			    const Dtype* top_diff = top[0]->cpu_diff();
			    Dtype* bottom_diff = bottom[0]->mutable_cpu_diff();
			    const int count = bottom[0]->count();
			    //Dtype negative_slope = this->layer_param_.relu_param().negative_slope();
			    for (int i = 0; i < count; ++i) {
			      bottom_diff[i] = std::max(top_diff[i],Dtype(0.));
			    }
		}
		break;
		default:
		{
			LOG(FATAL) << "unknown value for ro.relpropformulatype " << ro.relpropformulatype << std::endl;
			exit(1);
		}
		break;
		
	}
	
}



#ifdef CPU_ONLY
STUB_GPU(ReLULayer);
#endif

INSTANTIATE_CLASS(ReLULayer);

}  // namespace caffe
