from opentuner.search import technique
from opentuner.search.manipulator import IncrementableParameter


class SimpleTraverse(technique.ResumableSearchTechnique):
    """
    SimpleTraverse
        A simple search technique that traverses all the values of parameters
        Note: this technique does NOT traverse every single combination of
        parameter values.

        For example, if the seed config is {param1: 0, param2: 0, param3: 0}
        where each param has a search space of {0, 1, 2}.
        1st iteration: {param1: 0, param2: 0, param3: 0}
        2nd iteration: {param1: 1, param2: 0, param3: 0}
        3nd iteration: {param1: 2, param2: 0, param3: 0}
        4th iteration: {param1: 2, param2: 1, param3: 0}
        5th iteration: {param1: 2, param2: 2, param3: 0}
        6th iteration: {param1: 2, param2: 2, param3: 1}
        7th iteration: {param1: 2, param2: 2, param3: 2}
        END.

        Note: e.g. {param1: 0, param2: 2, param3: 2} is not explored by this
        technique.
    """

    def initial_step(self):
        # If this is the beginning of the recursion, use the seed_config.
        seed_config = self.manipulator.seed_config()
        db_config_obj = self.driver.get_configuration(seed_config)
        self.test_next(db_config_obj)
        # Use manipulator.copy() to create a new config to make sure
        # its corredsponding entry in db will be created by
        # driver.get_configuration() later.
        config = self.manipulator.copy(db_config_obj.data)

        parameters = self.manipulator.parameters(seed_config)
        for parameter in parameters:
            if not isinstance(parameter, IncrementableParameter):
                raise Exception(
                    parameter.__class__.__name__ + ' is not incrementable')

            start_val = parameter.get_value(config)
            next_value = parameter.next_value(config)

            while start_val != next_value:
                parameter.set_value(config, next_value)
                db_config_obj = self.driver.get_configuration(config)
                self.test_next(db_config_obj)
                # Create a new config.
                config = self.manipulator.copy(db_config_obj.data)
                next_value = parameter.next_value(config)


technique.register(SimpleTraverse())
