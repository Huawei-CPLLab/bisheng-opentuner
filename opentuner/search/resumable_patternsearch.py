import functools  # For python3 compatibility.
from opentuner.search import technique


class ResumablePatternSearch(technique.ResumableSearchTechnique):
  def initial_step(self):

    # start at a random position
    self.center = self.driver.get_configuration(self.manipulator.random())
    self.test_next(self.center)

    # initial step size is arbitrary
    self.step_size = 0.1
    self.add_callback(self.repeated_step)

  def repeated_step(self):
    self.points = list()
    for param in self.manipulator.parameters(self.center.data):
      if param.is_primitive():
        # get current value of param, scaled to be in range [0.0, 1.0]
        unit_value = param.get_unit_value(self.center.data)

        if unit_value > 0.0:
          # produce new config with param set step_size lower
          down_cfg = self.manipulator.copy(self.center.data)
          param.set_unit_value(down_cfg, max(0.0, unit_value - self.step_size))
          down_cfg = self.driver.get_configuration(down_cfg)
          self.test_next(down_cfg)
          self.points.append(down_cfg)

        if unit_value < 1.0:
          # produce new config with param set step_size higher
          up_cfg = self.manipulator.copy(self.center.data)
          param.set_unit_value(up_cfg, min(1.0, unit_value + self.step_size))
          up_cfg = self.driver.get_configuration(up_cfg)
          self.test_next(up_cfg)
          self.points.append(up_cfg)

      else:  # ComplexParameter
        for mutate_function in param.manipulators(self.center.data):
          cfg = self.manipulator.copy(self.center.data)
          mutate_function(cfg)
          cfg = self.driver.get_configuration(cfg)
          self.test_next(cfg)
          self.points.append(cfg)

    self.test_next(None)
    self.add_callback(self.repeated_step2)

  def repeated_step2(self):
    # sort points by quality, best point will be points[0], worst is points[-1]
    self.points.sort(key=functools.cmp_to_key(self.objective.compare))

    if (self.objective.lt(self.driver.best_result.configuration, self.center)
            and self.driver.best_result.configuration != self.points[0]):
      # another technique found a new global best, switch to that
      self.center = self.driver.best_result.configuration
    elif self.objective.lt(self.points[0], self.center):
      # we found a better point, move there
      self.center = self.points[0]
    else:
      # no better point, shrink the pattern
      self.step_size /= 2.0

    # Loop back to the repeated_step.
    self.add_callback(self.repeated_step)


# register our new technique in global list
technique.register(ResumablePatternSearch())
