from __future__ import print_function, division
import matplotlib
matplotlib.use('Agg') # Must be before importing matplotlib.pyplot or pylab!
from neuralnilm import Net, RealApplianceSource, BLSTMLayer, SubsampleLayer, DimshuffleLayer
from lasagne.nonlinearities import sigmoid, rectify
from lasagne.objectives import crossentropy, mse
from lasagne.init import Uniform, Normal
from lasagne.layers import LSTMLayer, DenseLayer, Conv1DLayer, ReshapeLayer
from lasagne.updates import adagrad, nesterov_momentum
from functools import partial
import os
from neuralnilm.source import standardise
from neuralnilm.experiment import run_experiment
from neuralnilm.net import TrainingError
import __main__

NAME = os.path.splitext(os.path.split(__main__.__file__)[1])[0]
PATH = "/homes/dk3810/workspace/python/neuralnilm/figures"
SAVE_PLOT_INTERVAL = 250
GRADIENT_STEPS = 100

"""
e92: Changes common to all these (compared to e91)
* on_power_thresh is now 20 watts for everything
* fixed max_appliance_powers and min_on_durations
* seq_length = 1500 (to fit in washer)
* min_on_durations increased for washer and dish washer
* skip_probability = 0.7

e94:
* Exactly the same experiments as e93 but using `gradient_steps=100` and 5000 epochs
* using `gradient_steps`
"""


def exp_a(name):
    """Results: Learning rate of 0.1 still NaNs."""

    """e91d but learning rate 0.01 
    and smaller inits (to try to capture 
    smaller changes) and larger first layer

    And e96 centres input data.  And I've fixed a problem where only the last
    instance of an appliance if multiple appliances occured within a batch would
    be shown in the targets.

    e98:
    Output just the fridge and use bool targets

    e99
    seq_length = 1000
    learning rate = 0.01 (tried 0.1 and 0.05 but both NaN'd)
    max_input_power = 500
    don't bother centering X
    only 50 units in first layer
    back to just 3 appliances
    skip prob = 0

    e100
    boolean_targets = False
    output_one_appliance=False

    e101
    max_input_power = 1000
    init back to Uniform(25)
    conv layer back to 20 filters

    e102
    n_seq_per_batch = 100  (50 ran.  500 got killed)
    """
    source = RealApplianceSource(
        filename='/data/dk3810/ukdale.h5',
        appliances=[
            ['fridge freezer', 'fridge', 'freezer'], 
            'hair straighteners', 
            'television'
            # 'dish washer',
            # ['washer dryer', 'washing machine']
        ],
        max_appliance_powers=[300, 500, 200], #, 2500, 2400],
        on_power_thresholds=[20, 20, 20], #, 20, 20],
        max_input_power=1000,
        min_on_durations=[60, 60, 60], #, 1800, 1800],
        window=("2013-06-01", "2014-07-01"),
        seq_length=1000,
        output_one_appliance=False,
        boolean_targets=False,
        min_off_duration=60,
        subsample_target=5,
        train_buildings=[1],
        validation_buildings=[1], 
        skip_probability=0,
        n_seq_per_batch=100
    )

    net = Net(
        experiment_name=name,
        source=source,
        save_plot_interval=SAVE_PLOT_INTERVAL,
        loss_function=crossentropy,
        updates=partial(nesterov_momentum, learning_rate=0.01),
        layers_config=[
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(25),
                'b': Uniform(25)
            },
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(10),
                'b': Uniform(10)
            },
            {
                'type': BLSTMLayer,
                'num_units': 40,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': Conv1DLayer,
                'num_filters': 20,
                'filter_length': 5,
                'stride': 5,
                'nonlinearity': sigmoid
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': BLSTMLayer,
                'num_units': 80,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DenseLayer,
                'num_units': source.n_outputs,
                'nonlinearity': sigmoid
            }
        ]
    )
    return net


def exp_b(name):
    # Same as A but with conv layer = 60 filters
    source = RealApplianceSource(
        filename='/data/dk3810/ukdale.h5',
        appliances=[
            ['fridge freezer', 'fridge', 'freezer'], 
            'hair straighteners', 
            'television'
            # 'dish washer',
            # ['washer dryer', 'washing machine']
        ],
        max_appliance_powers=[300, 500, 200], #, 2500, 2400],
        on_power_thresholds=[20, 20, 20], #, 20, 20],
        max_input_power=1000,
        min_on_durations=[60, 60, 60], #, 1800, 1800],
        window=("2013-06-01", "2014-07-01"),
        seq_length=1000,
        output_one_appliance=False,
        boolean_targets=False,
        min_off_duration=60,
        subsample_target=5,
        train_buildings=[1],
        validation_buildings=[1], 
        skip_probability=0,
        n_seq_per_batch=100
    )

    net = Net(
        experiment_name=name,
        source=source,
        save_plot_interval=SAVE_PLOT_INTERVAL,
        loss_function=crossentropy,
        updates=partial(nesterov_momentum, learning_rate=0.01),
        layers_config=[
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(25),
                'b': Uniform(25)
            },
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(10),
                'b': Uniform(10)
            },
            {
                'type': BLSTMLayer,
                'num_units': 40,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': Conv1DLayer,
                'num_filters': 60,
                'filter_length': 5,
                'stride': 5,
                'nonlinearity': sigmoid
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': BLSTMLayer,
                'num_units': 80,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DenseLayer,
                'num_units': source.n_outputs,
                'nonlinearity': sigmoid
            }
        ]
    )
    return net




def exp_c(name):
    # Same as A but with inits back to 10 and 5
    source = RealApplianceSource(
        filename='/data/dk3810/ukdale.h5',
        appliances=[
            ['fridge freezer', 'fridge', 'freezer'], 
            'hair straighteners', 
            'television'
            # 'dish washer',
            # ['washer dryer', 'washing machine']
        ],
        max_appliance_powers=[300, 500, 200], #, 2500, 2400],
        on_power_thresholds=[20, 20, 20], #, 20, 20],
        max_input_power=1000,
        min_on_durations=[60, 60, 60], #, 1800, 1800],
        window=("2013-06-01", "2014-07-01"),
        seq_length=1000,
        output_one_appliance=False,
        boolean_targets=False,
        min_off_duration=60,
        subsample_target=5,
        train_buildings=[1],
        validation_buildings=[1], 
        skip_probability=0,
        n_seq_per_batch=100
    )

    net = Net(
        experiment_name=name,
        source=source,
        save_plot_interval=SAVE_PLOT_INTERVAL,
        loss_function=crossentropy,
        updates=partial(nesterov_momentum, learning_rate=0.01),
        layers_config=[
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(10),
                'b': Uniform(10)
            },
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(5),
                'b': Uniform(5)
            },
            {
                'type': BLSTMLayer,
                'num_units': 40,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': Conv1DLayer,
                'num_filters': 20,
                'filter_length': 5,
                'stride': 5,
                'nonlinearity': sigmoid
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': BLSTMLayer,
                'num_units': 80,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DenseLayer,
                'num_units': source.n_outputs,
                'nonlinearity': sigmoid
            }
        ]
    )
    return net



def exp_d(name):
    # Same as A but max_input_power back to 500
    source = RealApplianceSource(
        filename='/data/dk3810/ukdale.h5',
        appliances=[
            ['fridge freezer', 'fridge', 'freezer'], 
            'hair straighteners', 
            'television'
            # 'dish washer',
            # ['washer dryer', 'washing machine']
        ],
        max_appliance_powers=[300, 500, 200], #, 2500, 2400],
        on_power_thresholds=[20, 20, 20], #, 20, 20],
        max_input_power=500,
        min_on_durations=[60, 60, 60], #, 1800, 1800],
        window=("2013-06-01", "2014-07-01"),
        seq_length=1000,
        output_one_appliance=False,
        boolean_targets=False,
        min_off_duration=60,
        subsample_target=5,
        train_buildings=[1],
        validation_buildings=[1], 
        skip_probability=0,
        n_seq_per_batch=100
    )

    net = Net(
        experiment_name=name,
        source=source,
        save_plot_interval=SAVE_PLOT_INTERVAL,
        loss_function=crossentropy,
        updates=partial(nesterov_momentum, learning_rate=0.01),
        layers_config=[
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(25),
                'b': Uniform(25)
            },
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(10),
                'b': Uniform(10)
            },
            {
                'type': BLSTMLayer,
                'num_units': 40,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': Conv1DLayer,
                'num_filters': 20,
                'filter_length': 5,
                'stride': 5,
                'nonlinearity': sigmoid
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': BLSTMLayer,
                'num_units': 80,
                'W_in_to_cell': Uniform(5),
                'gradient_steps': GRADIENT_STEPS
            },
            {
                'type': DenseLayer,
                'num_units': source.n_outputs,
                'nonlinearity': sigmoid
            }
        ]
    )
    return net



def exp_e(name):
    # Same as A but without gradient steps
    source = RealApplianceSource(
        filename='/data/dk3810/ukdale.h5',
        appliances=[
            ['fridge freezer', 'fridge', 'freezer'], 
            'hair straighteners', 
            'television'
            # 'dish washer',
            # ['washer dryer', 'washing machine']
        ],
        max_appliance_powers=[300, 500, 200], #, 2500, 2400],
        on_power_thresholds=[20, 20, 20], #, 20, 20],
        max_input_power=1000,
        min_on_durations=[60, 60, 60], #, 1800, 1800],
        window=("2013-06-01", "2014-07-01"),
        seq_length=1000,
        output_one_appliance=False,
        boolean_targets=False,
        min_off_duration=60,
        subsample_target=5,
        train_buildings=[1],
        validation_buildings=[1], 
        skip_probability=0,
        n_seq_per_batch=100
    )

    net = Net(
        experiment_name=name,
        source=source,
        save_plot_interval=SAVE_PLOT_INTERVAL,
        loss_function=crossentropy,
        updates=partial(nesterov_momentum, learning_rate=0.01),
        layers_config=[
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(25),
                'b': Uniform(25)
            },
            {
                'type': DenseLayer,
                'num_units': 50,
                'nonlinearity': sigmoid,
                'W': Uniform(10),
                'b': Uniform(10)
            },
            {
                'type': BLSTMLayer,
                'num_units': 40,
                'W_in_to_cell': Uniform(5)
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': Conv1DLayer,
                'num_filters': 20,
                'filter_length': 5,
                'stride': 5,
                'nonlinearity': sigmoid
            },
            {
                'type': DimshuffleLayer,
                'pattern': (0, 2, 1)
            },
            {
                'type': BLSTMLayer,
                'num_units': 80,
                'W_in_to_cell': Uniform(5)
            },
            {
                'type': DenseLayer,
                'num_units': source.n_outputs,
                'nonlinearity': sigmoid
            }
        ]
    )
    return net


def init_experiment(experiment):
    full_exp_name = NAME + experiment
    func_call = 'exp_{:s}(full_exp_name)'.format(experiment)
    print("***********************************")
    print("Preparing", full_exp_name, "...")
    net = eval(func_call)
    return net


def main():
    for experiment in list('abcdefgh'):
        full_exp_name = NAME + experiment
        path = os.path.join(PATH, full_exp_name)
        try:
            net = init_experiment(experiment)
            run_experiment(net, path)
        except KeyboardInterrupt:
            break
        except TrainingError as e:
            print("EXCEPTION:", e)


if __name__ == "__main__":
    main()
