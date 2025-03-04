import mesa
from mesa.agent import Agent
from mesa.model import Model
import contextlib
import copy
import operator
import weakref
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, MutableSet, Sequence
from random import Random
from typing import Any
from agents import BikerAgent


# THe following class is copied and then edited from the original mesa code base to make custom for this purpose of this biker agent model

class AgentSet:
    pass


class AgentSet(MutableSet, Sequence):
    """
    A collection class that represents an ordered set of agents within an agent-based model (ABM). This class
    extends both MutableSet and Sequence, providing set-like functionality with order preservation and
    sequence operations.

    Attributes:
        model (Model): The ABM model instance to which this AgentSet belongs.

    Methods:
        __len__, __iter__, __contains__, select, shuffle, sort, _update, do, get, __getitem__,
        add, discard, remove, __getstate__, __setstate__, random

    Note:
        The AgentSet maintains weak references to agents, allowing for efficient management of agent lifecycles
        without preventing garbage collection. It is associated with a specific model instance, enabling
        interactions with the model's environment and other agents.The implementation uses a WeakKeyDictionary to store agents,
        which means that agents not referenced elsewhere in the program may be automatically removed from the AgentSet.
    """

    agentset_experimental_warning_given = False

    def __init__(self, agents: Iterable[Agent], model: Model):
        """
        Initializes the AgentSet with a collection of agents and a reference to the model.

        Args:
            agents (Iterable[Agent]): An iterable of Agent objects to be included in the set.
            model (Model): The ABM model instance to which this AgentSet belongs.
        """

        self.model = model
        self._agents = weakref.WeakKeyDictionary({agent: None for agent in agents})

    def __len__(self) -> int:
        """Return the number of agents in the AgentSet."""
        return len(self._agents)

    def __iter__(self) -> Iterator[Agent]:
        """Provide an iterator over the agents in the AgentSet."""
        return self._agents.keys()

    def __contains__(self, agent: Agent) -> bool:
        """Check if an agent is in the AgentSet. Can be used like `agent in agentset`."""
        return agent in self._agents

    def select(
        self,
        filter_func: Callable[[Agent], bool] | None = None,
        n: int = 0,
        inplace: bool = False,
        agent_type: type[Agent] | None = None,
    ) -> AgentSet:
        """
        Select a subset of agents from the AgentSet based on a filter function and/or quantity limit.

        Args:
            filter_func (Callable[[Agent], bool], optional): A function that takes an Agent and returns True if the
                agent should be included in the result. Defaults to None, meaning no filtering is applied.
            n (int, optional): The number of agents to select. If 0, all matching agents are selected. Defaults to 0.
            inplace (bool, optional): If True, modifies the current AgentSet; otherwise, returns a new AgentSet. Defaults to False.
            agent_type (type[Agent], optional): The class type of the agents to select. Defaults to None, meaning no type filtering is applied.

        Returns:
            AgentSet: A new AgentSet containing the selected agents, unless inplace is True, in which case the current AgentSet is updated.
        """

        if filter_func is None and agent_type is None and n == 0:
            return self if inplace else copy.copy(self)

        def agent_generator(filter_func=None, agent_type=None, n=0):
            count = 0
            for agent in self:
                if (not filter_func or filter_func(agent)) and (
                    not agent_type or isinstance(agent, agent_type)
                ):
                    yield agent
                    count += 1
                    if 0 < n <= count:
                        break

        agents = agent_generator(filter_func, agent_type, n)

        return AgentSet(agents, self.model) if not inplace else self._update(agents)

    def shuffle(self, inplace: bool = False) -> AgentSet:
        """
        Randomly shuffle the order of agents in the AgentSet.

        Args:
            inplace (bool, optional): If True, shuffles the agents in the current AgentSet; otherwise, returns a new shuffled AgentSet. Defaults to False.

        Returns:
            AgentSet: A shuffled AgentSet. Returns the current AgentSet if inplace is True.

        Note:
            Using inplace = True is more performant

        """
        weakrefs = list(self._agents.keyrefs())
        self.random.shuffle(weakrefs)

        if inplace:
            self._agents.data = {entry: None for entry in weakrefs}
            return self
        else:
            return AgentSet(
                (agent for ref in weakrefs if (agent := ref()) is not None), self.model
            )

    def sort(
        self,
        key: Callable[[Agent], Any] | str,
        ascending: bool = False,
        inplace: bool = False,
    ) -> AgentSet:
        """
        Sort the agents in the AgentSet based on a specified attribute or custom function.

        Args:
            key (Callable[[Agent], Any] | str): A function or attribute name based on which the agents are sorted.
            ascending (bool, optional): If True, the agents are sorted in ascending order. Defaults to False.
            inplace (bool, optional): If True, sorts the agents in the current AgentSet; otherwise, returns a new sorted AgentSet. Defaults to False.

        Returns:
            AgentSet: A sorted AgentSet. Returns the current AgentSet if inplace is True.
        """
        if isinstance(key, str):
            key = operator.attrgetter(key)

        sorted_agents = sorted(self._agents.keys(), key=key, reverse=not ascending)

        return (
            AgentSet(sorted_agents, self.model)
            if not inplace
            else self._update(sorted_agents)
        )

    def _update(self, agents: Iterable[Agent]):
        """Update the AgentSet with a new set of agents.
        This is a private method primarily used internally by other methods like select, shuffle, and sort.
        """

        self._agents = weakref.WeakKeyDictionary({agent: None for agent in agents})
        return self

    def do(
        self, method_name: str, *args, return_results: bool = False, **kwargs
    ) -> AgentSet | list[Any]:
        """
        Invoke a method on each agent in the AgentSet.

        Args:
            method_name (str): The name of the method to call on each agent.
            return_results (bool, optional): If True, returns the results of the method calls; otherwise, returns the AgentSet itself. Defaults to False, so you can chain method calls.
            *args: Variable length argument list passed to the method being called.
            **kwargs: Arbitrary keyword arguments passed to the method being called.

        Returns:
            AgentSet | list[Any]: The results of the method calls if return_results is True, otherwise the AgentSet itself.
        """
        # we iterate over the actual weakref keys and check if weakref is alive before calling the method
        res = [
            getattr(agent, method_name)(*args, **kwargs)
            for agentref in self._agents.keyrefs()
            if (agent := agentref()) is not None
        ]

        return res if return_results else self

    def get(self, attr_names: str | list[str]) -> list[Any]:
        """
        Retrieve the specified attribute(s) from each agent in the AgentSet.

        Args:
            attr_names (str | list[str]): The name(s) of the attribute(s) to retrieve from each agent.

        Returns:
            list[Any]: A list with the attribute value for each agent in the set if attr_names is a str
            list[list[Any]]: A list with a list of attribute values for each agent in the set if attr_names is a list of str

        Raises:
            AttributeError if an agent does not have the specified attribute(s)

        """

        if isinstance(attr_names, str):
            return [getattr(agent, attr_names) for agent in self._agents]
        else:
            return [
                [getattr(agent, attr_name) for attr_name in attr_names]
                for agent in self._agents
            ]

    def __getitem__(self, item: int | slice) -> Agent:
        """
        Retrieve an agent or a slice of agents from the AgentSet.

        Args:
            item (int | slice): The index or slice for selecting agents.

        Returns:
            Agent | list[Agent]: The selected agent or list of agents based on the index or slice provided.
        """
        return list(self._agents.keys())[item]

    def add(self, agent: Agent):
        """
        Add an agent to the AgentSet.

        Args:
            agent (Agent): The agent to add to the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        self._agents[agent] = None

    def discard(self, agent: Agent):
        """
        Remove an agent from the AgentSet if it exists.

        This method does not raise an error if the agent is not present.

        Args:
            agent (Agent): The agent to remove from the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        with contextlib.suppress(KeyError):
            del self._agents[agent]

    def remove(self, agent: Agent):
        """
        Remove an agent from the AgentSet.

        This method raises an error if the agent is not present.

        Args:
            agent (Agent): The agent to remove from the set.

        Note:
            This method is an implementation of the abstract method from MutableSet.
        """
        del self._agents[agent]

    def __getstate__(self):
        """
        Retrieve the state of the AgentSet for serialization.

        Returns:
            dict: A dictionary representing the state of the AgentSet.
        """
        return {"agents": list(self._agents.keys()), "model": self.model}

    def __setstate__(self, state):
        """
        Set the state of the AgentSet during deserialization.

        Args:
            state (dict): A dictionary representing the state to restore.
        """
        self.model = state["model"]
        self._update(state["agents"])

    @property
    def random(self) -> Random:
        """
        Provide access to the model's random number generator.

        Returns:
            Random: The random number generator associated with the model.
        """
        return self.model.random


class CustomScheduler(mesa.time.BaseScheduler):
    """
        A scheduler that activates each type of agent once per step, in random order, with the order reshuffled every step.

        This scheduler is useful for models with multiple types of agents, ensuring that each type is treated
        equitably in terms of activation order. The randomness in activation order helps in reducing biases
        due to ordering effects.

        Inherits all attributes and methods from BaseScheduler.

        If you want to do some computations / data collections specific to an agent
        type, you can either:
        - loop through all agents, and filter by their type
        - access via `your_model.scheduler.agents_by_type[your_type_class]`

        Attributes:
            - agents_by_type (defaultdict): A dictionary mapping agent types to dictionaries of agents.

        Methods:
            - step: Executes the step of each agent type in a random order.
            - step_type: Activates all agents of a given type.
            - get_type_count: Returns the count of agents of a specific type.
        """

    @property
    def agents_by_type(self):
        # warnings.warn(
        #     "Because of the shift to using AgentSet, in the future this attribute will return a dict with"
        #     "type as key as AgentSet as value. Future behavior is available via RandomActivationByType._agents_by_type",
        #     DeprecationWarning,
        #     stacklevel=2,
        # )

        agentsbytype = defaultdict(dict)
        for k, v in self._agents_by_type.items():
            agentsbytype[k] = {agent.unique_id: agent for agent in v}

        return agentsbytype

    def __init__(self, model: Model, agents: Iterable[Agent] | None = None) -> None:
        super().__init__(model)
        """

        Args:
            model (Model): The model to which the schedule belongs
            agents (Iterable[Agent], None, optional): An iterable of agents who are controlled by the schedule
        """

        # can't be a defaultdict because we need to pass model to AgentSet
        self._agents_by_type: [type, AgentSet] = {}

        if agents is not None:
            for agent in agents:
                try:
                    self._agents_by_type[type(agent)].add(agent)
                except KeyError:
                    self._agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def add(self, agent: Agent) -> None:
        """
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        """
        super().add(agent)

        try:
            self._agents_by_type[type(agent)].add(agent)
        except KeyError:
            self._agents_by_type[type(agent)] = AgentSet([agent], self.model)

    def remove(self, agent: Agent) -> None:
        """
        Remove all instances of a given agent from the schedule.
        """
        super().remove(agent)
        self._agents_by_type[type(agent)].remove(agent)

    def step(self) -> None:
        """
        Executes the step of each agent type, one at a time, in random order.

        Args:
            shuffle_types: If True, the order of execution of each types is
                           shuffled.
            shuffle_agents: If True, the order of execution of each agents in a
                            type group is shuffled.
        """
        # To be able to remove and/or add agents during stepping
        # it's necessary to cast the keys view to a list.
        # type_keys: list[type[Agent]] = list(self._agents_by_type.keys())
        # if shuffle_types:
        #     self.model.random.shuffle(type_keys)
        # for agent_class in type_keys:
        # Step bikers first then road
        self.step_type(BikerAgent)
        #self.step_type(agent_class, shuffle_agents=shuffle_agents)
        self.steps += 1
        self.time += 1

    def step_type(self, agenttype: type[Agent]) -> None:
        """
        Shuffle order and run all agents of a given type.
        This method is equivalent to the NetLogo 'ask [breed]...'.

        Args:
            agenttype: Class object of the type to run.
        """
        agents = self._agents_by_type[agenttype]
        agents.do("step")

    def get_type_count(self, agenttype: type[Agent]) -> int:
        """
        Returns the current number of agents of certain type in the queue.
        """
        return len(self._agents_by_type[agenttype])