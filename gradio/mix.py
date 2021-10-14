"""
Ways to transform interfaces to produce new interfaces
"""
import gradio

class Parallel(gradio.Interface):
    """
    Creates a new Interface consisting of multiple models in parallel
    Parameters: 
    interfaces: any number of Interface objects that are to be compared in parallel 
    options: additional kwargs that are passed into the new Interface object to customize it  
    Returns:
    (Interface): an Interface object comparing the given models
    """
    def __init__(self, *interfaces, **options):
        fns = []
        outputs = []
        
        for io in interfaces:
            fns.extend(io.predict)
            outputs.extend(io.output_components)

        kwargs = {
            "fn": fns,
            "inputs": interfaces[0].input_components,
            "outputs": outputs,
            "repeat_outputs_per_model": False,
        }
        kwargs.update(options)
        super().__init__(**kwargs) 


class Series(gradio.Interface):
    """
    Creates a new Interface from multiple models in series (the output of one is fed as the input to the next)
    Parameters: 
    interfaces: any number of Interface objects that are to be connected in series 
    options: additional kwargs that are passed into the new Interface object to customize it  
    Returns:
    (Interface): an Interface object connecting the given models
    """
    def __init__(self, *interfaces, **options):
        fns = [io.predict for io in interfaces]
    
        def connected_fn(*data):  # Run each function with the appropriate preprocessing and postprocessing 
            for idx, io in enumerate(interfaces):
                # skip preprocessing for first interface since the compound interface will include it
                if idx > 0:
                    data = [input_interface.preprocess(data[i]) for i, input_interface in enumerate(io.input_components)]
                # run all of predictions sequentially
                predictions = []
                for predict_fn in io.predict:
                    prediction = predict_fn(*data)
                    predictions.append(prediction)
                data = predictions
                # skip postprocessing for final interface since the compound interface will include it
                if idx < len(interfaces) - 1:
                    data = [output_interface.postprocess(data[i]) for i, output_interface in enumerate(io.output_components)]
            return data[0]
    
        connected_fn.__name__ = " => ".join([f[0].__name__ for f in fns])

        kwargs = {
            "fn": connected_fn,
            "inputs": interfaces[0].input_components,
            "outputs": interfaces[-1].output_components,
        }
        kwargs.update(options)
        super().__init__(**kwargs) 


class DAG(gradio.Interface):
    """
    Defines a DAG-based structure that allows for connecting Interfaces together in various ways
    TODO(abidlabs):
    1. Handle empty DAG in launch()
    2. Handle killing outputs
    3. Setting inputs to constant values
    """

    def connect(out, inp):
        """
        out: Interface, or (Interface, index), or Constant
        in: Interface, or (Interface, index), or Null
        TODO(abidlabs): Implement this
        - Should check to make sure types are valid, or raise an error (but 
        some collapsing might be okay. For example Label --> Text)
        """
        pass

    def expose(out):
        """
        out: Interface, or (Interface, index)
        TODO(abidlabs): Implement this
        """
        pass

    def visualize():
        """
        Draw a matplotlib rendering of the graph (can assume relatively small dag)
        TODO: low priority
        """
        pass

class Constant():
    def __init__(self, value):
        self.value = value

class Null():
    def __init__(self):
        pass