package edu.stanford.cs224w.project;

public class WeightedEdge
{
	private String name;
	private double weight;
	
	public WeightedEdge(String name, double weight)
   {
	   super();
	   this.name = name;
	   this.weight = weight;
   }

	public String getName()
	{
		return name;
	}

	public void setName(String name)
	{
		this.name = name;
	}

	public double getWeight()
	{
		return weight;
	}

	public void setWeight(double weight)
	{
		this.weight = weight;
	}

	@Override
   public int hashCode()
   {
	   final int prime = 31;
	   int result = 1;
	   result = prime * result + ((name == null) ? 0 : name.hashCode());
	   long temp;
	   temp = Double.doubleToLongBits(weight);
	   result = prime * result + (int) (temp ^ (temp >>> 32));
	   return result;
   }

	@Override
   public boolean equals(Object obj)
   {
	   if (this == obj)
		   return true;
	   if (obj == null)
		   return false;
	   if (getClass() != obj.getClass())
		   return false;
	   WeightedEdge other = (WeightedEdge) obj;
	   if (name == null)
	   {
		   if (other.name != null)
			   return false;
	   }
	   else if (!name.equals(other.name))
		   return false;
	   if (Double.doubleToLongBits(weight) != Double.doubleToLongBits(other.weight))
		   return false;
	   return true;
   }

	@Override
   public String toString()
   {
	   StringBuilder builder = new StringBuilder();
	   builder.append("WeightedEdge [name=");
	   builder.append(name);
	   builder.append(", weight=");
	   builder.append(weight);
	   builder.append("]");
	   return builder.toString();
   }

}
