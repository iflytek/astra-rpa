from unittest import TestCase

from rpa_executor.flow.syntax.environment import EnvBizTypes, Environment, EnvItem


class TestEnvironment(TestCase):
    def test_getitem_1(self):
        env = Environment()
        env.setitem("a", EnvItem(biz_types=EnvBizTypes.Global, key="a", value=1))
        env.setitem("b", EnvItem(biz_types=EnvBizTypes.Flow, key="b", value=2))
        env = env.new_enclose_environment()
        env.setitem("a", EnvItem(biz_types=EnvBizTypes.Flow, key="a", value=4))
        env.setitem("a", EnvItem(biz_types=EnvBizTypes.Global, key="a", value=3))
        env = env.new_enclose_environment()
        env = env.new_enclose_environment()
        env = env.new_enclose_environment()
        env = env.new_enclose_environment()
        d = env.to_dict()
        p = env.getitem("a")
        print(d)
